# Research Group: subset-b-004327

This grouped report covers the requested DSA switch-driver subset. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/seville_vsc9953.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/seville_vsc9953.c

## Purpose

This file is the DSA platform driver for the Microchip/Microsemi VSC9953 "Seville" switch block, using the shared Ocelot/Felix infrastructure. It describes the VSC9953 register layout, VCAP capabilities, port modes, reset sequence, internal MDIO/PCS discovery, and the platform probe/remove/shutdown hooks that register the switch as a Felix-backed DSA device with `DSA_TAG_PROTO_SEVILLE`.

## Important APIs, Types, and Data

- `VSC9953_NUM_PORTS` is 10. Ports 0-7 support serial PCS modes (`1000BASEX`, `SGMII`, `QSGMII`), while ports 8-9 are internal.
- `vsc9953_*_regmap` arrays map Ocelot logical registers for ANA, QS, VCAP, QSYS, REW, SYS, GCB, and DEV_GMII targets to VSC9953 offsets. Unsupported registers are explicitly reserved.
- `vsc9953_resources` and `vsc9953_resource_names` describe the target memory windows relative to the platform resource base. These are consumed by `felix_register_switch()`.
- `vsc9953_regfields` maps shared Ocelot regfield IDs to VSC9953 bit positions, including reset, MAC-table, pause, extraction/injection header, and per-port switch mode fields.
- `vsc9953_vcap_*_keys`, `vsc9953_vcap_*_actions`, and `vsc9953_vcap_props` describe ES0, IS1, and IS2 key/action widths and target blocks for Ocelot VCAP handling.
- `vsc9953_ops` implements the `struct ocelot_ops` hooks for reset, watermark encode/decode/stat parsing, and Felix netdev/port translation.
- `seville_info_vsc9953` is the central `struct felix_info` instance tying together resources, register maps, regfields, VCAP, policer ranges, MAC-table size, port count, quirks, MDIO callbacks, and port modes.

## Control Flow

Probe starts in `seville_probe()`, validates the platform memory resource, and calls `felix_register_switch(dev, res->start, 1, false, false, DSA_TAG_PROTO_SEVILLE, &seville_info_vsc9953)`. Felix then uses the static metadata in this file to map target windows, initialize Ocelot state, reset the switch, and register the DSA switch.

The reset hook `vsc9953_reset()` soft-resets the switch core through `GCB_SOFT_RST_SWC_RST`, waits for the bit to clear, enables and triggers SYS memory initialization, waits for `SYS_RESET_CFG_MEM_INIT` to clear, then enables the switch core with `SYS_RESET_CFG_CORE_ENA`. Polling uses `readx_poll_timeout()` via small status helpers.

MDIO setup is handled by `vsc9953_mdio_bus_alloc()`. It allocates `felix->pcs`, creates an internal MIIM bus through `mscc_miim_setup()` using GCB registers, registers that bus with OF MDIO helpers, and then scans non-unused, non-internal ports for Lynx PCS devices at internal MDIO addresses `port + 4`. `vsc9953_mdio_bus_free()` destroys any created PCS objects; bus unregister/free are device-managed.

Remove and shutdown are DSA lifecycle wrappers. `seville_remove()` calls `dsa_unregister_switch()` when a Felix instance exists. `seville_shutdown()` calls `dsa_switch_shutdown()` and clears platform drvdata.

## State and Persistence

Persistent runtime state is held by the Felix/Ocelot core, not by file-local mutable globals. This file contributes static hardware description tables. Runtime state created here includes the device-managed internal MDIO bus, the `felix->pcs` array, and per-port Lynx PCS instances. Hardware state persists in switch registers until reset/shutdown, including VCAP entries, MAC table, pause configuration, and port modes configured by the Ocelot/Felix stack.

## Dependencies and Integration Points

The driver depends on Linux platform devices, OF matching, DSA, phylink PCS, `pcs-lynx`, `mdio-mscc-miim`, and the Ocelot/Felix common driver. It integrates with DSA via `felix_register_switch()`, with Ocelot through register maps/regfields/VCAP props, and with internal SerDes/PCS through an MDIO bus. The OF compatible string is `mscc,vsc9953-switch`.

## Risks and Edge Cases

The largest risk is register-description accuracy: bad offsets, field widths, or resource names can silently corrupt switch configuration. Reset sequencing depends on timeout constants and assumes GCB/SYS bits behave as expected. PCS discovery ignores failed `lynx_pcs_create_mdiodev()` calls per port, which allows partial operation but can obscure missing PCS instances. Port-mode mismatch in device tree can leave serial ports without PCS support. The watermark encoder warns on values outside the representable range but still returns an encoded value, so callers must respect hardware limits.

## Test Signals

Useful signals are successful platform probe on a `mscc,vsc9953-switch` node, DSA switch registration with 10 ports, internal MDIO bus registration, "Found PCS" messages for active serial ports, successful link-up over SGMII/QSGMII/1000BASE-X, VCAP rule programming through switchdev/tc, FDB learning, bridge/VLAN behavior through the Ocelot stack, and clean remove/shutdown without leaked PCS objects. Negative tests should cover reset timeouts, absent platform resources, missing MDIO/PCS devices, unused ports, and register access failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/seville_vsc9953.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/Kconfig

## Purpose

This Kconfig file exposes build-time options for Qualcomm/Atheros DSA switch drivers in this directory: the AR9331 embedded switch, the QCA8K family driver, and optional QCA8K LED support.

## Important APIs, Types, and Functions

- `NET_DSA_AR9331` is a tristate option that depends on `NET_DSA` and selects `NET_DSA_TAG_AR9331` and `REGMAP`.
- `NET_DSA_QCA8K` is a tristate option that selects the QCA DSA tagger and `REGMAP`.
- `NET_DSA_QCA8K_LEDS_SUPPORT` is a bool depending on `NET_DSA_QCA8K`, compatible LED class linkage, and `LEDS_TRIGGERS`.

## Control Flow

There is no runtime control flow. The file controls Kconfig dependency resolution. Enabling AR9331 or QCA8K makes the corresponding object buildable; LED support is compiled into the QCA8K composite object only when the LED option is enabled.

## State and Persistence

State is limited to kernel configuration values. Those values persist in the generated `.config` and determine which object files and tag protocol helpers are included.

## Dependencies and Integration Points

The options integrate with the DSA subsystem, DSA tag protocol modules (`tag_ar9331`, `tag_qca`), regmap, and the LED subsystem. `NET_DSA_QCA8K_LEDS_SUPPORT` explicitly handles built-in/module compatibility by allowing `LEDS_CLASS=y` or `LEDS_CLASS=NET_DSA_QCA8K`.

## Risks and Edge Cases

Incorrect dependencies can produce link failures, especially for LED class symbols or tagger support. The help text for LED support says "This enabled support" rather than "enables"; cosmetic only. QCA8K does not explicitly depend on `NET_DSA` in this file, so it relies on its menu context or higher-level DSA Kconfig inclusion to make the option meaningful.

## Test Signals

Build matrix signals include `NET_DSA_AR9331=m/y`, `NET_DSA_QCA8K=m/y`, LED support built in and disabled, and module/built-in combinations for `LEDS_CLASS`. Runtime signals are availability of matching DSA taggers and absence of unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/Makefile

## Purpose

This Makefile maps the QCA DSA Kconfig symbols to object files. It builds AR9331 as a standalone object and QCA8K as a composite module/object.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_NET_DSA_AR9331) += ar9331.o`
- `obj-$(CONFIG_NET_DSA_QCA8K) += qca8k.o`
- `qca8k-y += qca8k-common.o qca8k-8xxx.o`
- `qca8k-y += qca8k-leds.o` when `CONFIG_NET_DSA_QCA8K_LEDS_SUPPORT` is set.

## Control Flow

There is no runtime control flow. Kbuild combines the listed objects into `qca8k.o` when QCA8K is enabled and conditionally includes the LED implementation.

## State and Persistence

The file affects build artifacts only. No runtime state is introduced.

## Dependencies and Integration Points

It integrates with Kbuild and the symbols declared in the local Kconfig. The composite object arrangement lets `qca8k-common.c`, `qca8k-8xxx.c`, and optionally `qca8k-leds.c` share internal headers and one module registration unit.

## Risks and Edge Cases

The conditional `ifdef CONFIG_NET_DSA_QCA8K_LEDS_SUPPORT` must match Kconfig exactly; otherwise `qca8k_setup_led_ctrl()` would resolve to the inline stub in `qca8k_leds.h` or fail to link if declarations diverge. Object order is conventional: common code before the device-specific driver. Build-only changes here need all tristate combinations tested.

## Test Signals

Expected build outputs are `ar9331.o` when AR9331 is enabled and `qca8k.o` containing `qca8k-common.o` plus `qca8k-8xxx.o`, with `qca8k-leds.o` present only for LED support. `modinfo qca8k` should reflect the module metadata from `qca8k-8xxx.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/ar9331.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/ar9331.c

## Purpose

This file implements the DSA driver for the Qualcomm Atheros AR9331 built-in Ethernet switch. It presents the six-port switch to DSA, handles indirect MDIO/regmap access to 32-bit switch registers over a 16-bit MDIO protocol, initializes switch forwarding, exposes an internal MDIO master for PHY access, manages a nested PHY interrupt domain, and accumulates hardware MIB counters into Linux statistics.

## Important APIs, Types, and Functions

- `struct ar9331_sw_priv` holds device, DSA switch, IRQ domain/mask, MDIO master/slave buses, regmap, reset control, and six per-port state structures.
- `struct ar9331_sw_port` holds the port index, delayed MIB polling work, accumulated `rtnl_link_stats64`, pause stats, and stats spinlock.
- `struct ar9331_sw_stats_raw` mirrors the hardware MIB block layout read with `regmap_bulk_read()`.
- `ar9331_sw_reset()`, `ar9331_sw_setup()`, and `ar9331_sw_setup_port()` initialize hardware, MDIO bus, max frame size, broadcast forwarding, VLAN/member masks, and CPU-header mode.
- `ar9331_sw_mbus_read()` and `ar9331_sw_mbus_write()` expose the switch's MDIO master through the child `mdio` bus.
- `ar9331_mdio_read()`, `ar9331_mdio_write()`, and `ar9331_sw_bus` implement regmap transport over the parent MDIO bus, including page selection and split 32-bit accesses.
- `ar9331_phylink_mac_ops` and `ar9331_sw_ops` connect phylink and DSA callbacks.
- `ar9331_sw_irq_init()` creates a one-cell IRQ domain for PHY interrupts sourced from switch global interrupt status.
- `ar9331_sw_probe()`, `ar9331_sw_remove()`, and `ar9331_sw_shutdown()` implement the MDIO driver lifecycle.

## Control Flow

Probe allocates `ar9331_sw_priv`, initializes a regmap on top of `ar9331_sw_bus`, obtains the `"switch"` reset control, stores the parent MDIO bus as `sbus`, initializes IRQ handling, populates the embedded `dsa_switch`, initializes per-port stats locks and delayed work, then calls `dsa_register_switch()`.

DSA setup resets the switch, registers the child MDIO bus from the `mdio` child node, allows broadcast frames to reach CPU, sets the global max frame size, and initializes every port. CPU ports get a membership mask for all user ports plus the AR9331 header bit. User ports get a membership mask containing only the upstream CPU port. Other ports are isolated.

Phylink advertises GMII and 1000M capability on port 0, and internal 10/100 capability on ports 1-5. `mac_config` disables hardware link/flow auto configuration. `mac_link_up` schedules immediate MIB polling and writes speed, duplex, flow control, and MAC enable bits. `mac_link_down` clears TX/RX MAC enable bits and cancels stats polling.

Regmap access works by using a synthetic page register (`AR9331_SW_REG_PAGE`) and regmap range config. Reads split a 32-bit register into two 16-bit MDIO reads. Writes send the high half before the low half because trigger bits can live in the low half while parameters live in the high half.

The IRQ path reads `AR9331_SW_REG_GINT`, maps `AR9331_SW_GINT_PHY_INT` to child IRQ 0, handles it nested, and acknowledges by writing the status back. Mask changes are serialized by `lock_irq` and applied to `AR9331_SW_REG_GINT_MASK`.

## State and Persistence

The driver maintains accumulated stats in memory because AR9331 MIB counters are cleared on read and are only 32-bit. Delayed work periodically reads and accumulates counters while links are up. `irq_mask` caches the desired PHY interrupt mask before sync. Regmap uses `REGCACHE_MAPLE`; the synthetic page register is treated as nonvolatile so regmap can cache it, but reset invalidates hardware page state. Hardware switch state includes port member masks, port status, global frame size, flood mask, and interrupt masks.

## Dependencies and Integration Points

This file depends on DSA, phylink, OF IRQ/MDIO, regmap, reset controls, MDIO driver registration, and the AR9331 DSA tagger. It integrates with device tree compatible `qca,ar9331-switch`, expects an OF `mdio` child node for internal PHY registration, and exposes nested PHY interrupts through an IRQ domain.

## Risks and Edge Cases

The 20 microsecond MDIO busy timeout is short and hardware-sensitive. Reset clears the page-selector state, so any future optimization that assumes cached page state must be careful. `ar9331_mdio_read()` returns all bits set for the synthetic page register so first access rewrites the page; this is intentional but easy to break. Stats are only polled while links are up, so missed link transitions can affect accumulation. IRQ setup requires a parent IRQ and creates only one child interrupt. Remove cancels work before unregistering but also asserts reset, which can disrupt shared hardware assumptions on embedded SoCs.

## Test Signals

Test signals include successful MDIO driver probe for `qca,ar9331-switch`, child MDIO bus registration, DSA switch registration with six ports, correct AR9331-tagged traffic through the CPU port, link-up/down updating port status, MIB counters increasing without wrap-induced loss under polling, nested PHY interrupt delivery, and clean remove/shutdown. Negative cases should cover missing reset control, missing `mdio` child, parent IRQ absence, MDIO page/register access failures, and rapid link flapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/ar9331.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k-8xxx.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k-8xxx.c

## Purpose

This file is the device-specific QCA8K DSA driver for QCA8327/QCA8328/QCA8334/QCA8337 switches. It implements register transport over MDIO and optional QCA management Ethernet packets, internal PHY MDIO access, device-tree parsing for CPU ports and power/LED settings, phylink and PCS handling, switch setup, management-packet MIB acceleration, probe/remove/shutdown, and suspend/resume.

## Important APIs, Types, and Functions

- `qca8k_split_addr()`, `qca8k_set_page()`, `qca8k_read_mii()`, and `qca8k_write_mii()` implement paged 32-bit register access over the MDIO bus.
- `qca8k_alloc_mdio_header()`, `qca8k_read_eth()`, `qca8k_write_eth()`, and `qca8k_rw_reg_ack_handler()` implement register reads/writes through QCA tagged management Ethernet frames when a CPU-port-0 conduit is operational.
- `qca8k_phy_eth_command()`, `qca8k_mdio_read()`, and `qca8k_mdio_write()` access internal PHY registers through the switch MDIO master, using Ethernet management first and falling back to MDIO.
- `qca8k_mdio_register()` and `qca8k_setup_mdio_bus()` register the internal/user MDIO bus and reject mixed internal/external PHY configurations.
- `qca8k_parse_port_config()`, `qca8k_mac_config_setup_internal_delay()`, `qca8k_phylink_mac_config()`, and `qca8k_pcs_config()` configure RGMII/SGMII delays, PLL, clock edge, SerDes mode, and PCS behavior.
- `qca8k_setup()` is the main DSA setup routine.
- `qca8k_switch_ops` wires common QCA8K DSA callbacks from `qca8k-common.c` plus local phylink, tagger, conduit, and LAG-related callbacks.
- `qca8k_sw_probe()`, `qca8k_sw_remove()`, `qca8k_sw_shutdown()`, `qca8k_suspend()`, and `qca8k_resume()` implement MDIO driver lifecycle and PM.
- `qca8327`, `qca8328`, and `qca833x` provide match data for device IDs, package mode, MIB count, and optional Ethernet MIB operations.

## Control Flow

Probe allocates `qca8k_priv`, stores the parent MDIO bus and OF match data, toggles optional reset GPIO, creates a no-cache regmap using custom bulk read/write/update callbacks, initializes the MDIO page cache to invalid, reads and validates the switch ID, allocates `dsa_switch`, initializes management and MIB completions/mutexes, fills DSA ops/phylink ops, initializes `reg_mutex`, stores drvdata, and registers the switch.

The regmap read/write path tries Ethernet management access when `priv->mgmt_conduit` is available, then falls back to paged MDIO. Management Ethernet packets are QCA-tagged frames with sequence numbers and completions; ACK handlers are installed through `qca8k_connect_tag_protocol()`. Internal PHY reads/writes similarly prefer Ethernet management command packets and fall back to MDIO master register access.

DSA setup finds a CPU port (0 preferred, 6 fallback), parses CPU-port RGMII/SGMII delay and clock settings, configures the internal MDIO bus, applies PWS and SoC-specific MAC power selection, registers LED class devices, initializes PCS objects, disables MAC06 exchange, enables CPU forwarding, initializes MIB counters, disables forwarding and user MACs by default, enables QCA header mode on CPU ports, routes unknown/broadcast/multicast/IGMP frames to the selected CPU port, programs CPU and user port membership, applies QCA8337 HOL fixups and QCA8327 flow-control thresholds, sets default max frame size, flushes FDB, and publishes ageing/LAG limits.

Phylink setup advertises RGMII/SGMII capabilities on CPU ports 0/6 and internal PHY modes on user ports. Link-up writes the port status register with speed, duplex, pause, and MAC enable bits unless in-band negotiation is used. PCS polling reads `QCA8K_REG_PORT_STATUS`; PCS config controls SerDes auto-negotiation, SGMII mode, PLL, delays, and clock edge bits.

## State and Persistence

Runtime state lives in `struct qca8k_priv`: switch ID/revision, mirror flags, LAG hash mode, enabled-port bitmap, isolation bitmap, parsed port delays, regmap, buses, DSA switch pointer, management conduit, Ethernet management sequence/ack/completion buffers, MIB autocast state, MDIO page cache, PCS objects, and LED objects. Hardware state includes CPU forwarding, port member masks, VLAN defaults, header mode, HOL thresholds, PWS settings, MIB enablement, SGMII/RGMII pad controls, and FDB contents. Suspend/resume uses `port_enabled_map` to disable and later re-enable only ports that were active before suspend.

## Dependencies and Integration Points

The driver depends on Linux DSA, phylink/PCS, MDIO, OF, GPIO reset, regmap, QCA tagger metadata from `linux/dsa/tag_qca.h`, netdevice management packet delivery, LED support through `qca8k_leds.h`, and shared QCA8K common functions. It integrates with compatible strings `qca,qca8327`, `qca,qca8328`, `qca,qca8334`, and `qca,qca8337`.

## Risks and Edge Cases

The transport path is complex: Ethernet management and MDIO access share sequence numbers, completions, mutexes, and fallback behavior. `qca8k_bulk_read()` and write paths rely on `mgmt_conduit` state being changed under the same management mutexes. Mixed internal and external PHY configurations are rejected because enabling MDIO master disconnects external MDC passthrough. CPU port 0 is required for Ethernet management acceleration. SGMII PLL and delay settings have chip/revision-specific warnings and restrictions. The QCA8337 HOL fixup and QCA8327 flow-control thresholds are hardware-workaround sensitive. In `qca8k_pcs_config()`, the final `ret` from clock-edge `qca8k_rmw()` is not returned, so that failure is not propagated.

## Test Signals

Strong signals are successful probe and switch ID validation for each compatible, DSA registration with seven ports, working QCA tag protocol callbacks, traffic through CPU port 0 and/or 6, internal MDIO bus registration in both explicit and legacy modes, rejection of mixed internal/external PHY DT layouts, RGMII/SGMII link-up with correct delays, management Ethernet read/write fallback behavior, MIB autocast stats, LED registration when enabled, VLAN/FDB/bridge/LAG behavior through common ops, suspend/resume preserving enabled ports, and clean remove/shutdown disabling ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k-8xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k-common.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k-common.c

## Purpose

This file contains shared QCA8K switch operations used by the QCA8K device driver: basic regmap wrappers, MIB descriptor data, FDB and VLAN table programming, ethtool stats, EEE configuration, bridge/STP membership handling, port enable/disable and MTU, ageing, MDB/mirror operations, VLAN callbacks, LAG offload, and switch ID validation.

## Important APIs, Types, and Functions

- `ar8327_mib[]` describes QCA832x/QCA833x MIB counter names, offsets, and 32/64-bit sizes.
- `qca8k_read()`, `qca8k_write()`, and `qca8k_rmw()` wrap `regmap_read/write/update_bits`.
- `qca8k_readable_table` constrains valid readable register ranges for the QCA8K regmap.
- FDB helpers include `qca8k_fdb_read()`, `qca8k_fdb_write()`, `qca8k_fdb_access()`, `qca8k_fdb_next()`, `qca8k_fdb_add()`, `qca8k_fdb_del()`, `qca8k_fdb_search_and_insert()`, `qca8k_fdb_search_and_del()`, and public DSA callbacks.
- VLAN helpers include `qca8k_vlan_access()`, `qca8k_vlan_add()`, `qca8k_vlan_del()`, and DSA VLAN callbacks.
- Bridge and port state APIs include `qca8k_port_stp_state_set()`, `qca8k_port_bridge_flags()`, `qca8k_port_bridge_join()`, `qca8k_port_bridge_leave()`, `qca8k_port_enable()`, and `qca8k_port_disable()`.
- LAG helpers include `qca8k_lag_can_offload()`, `qca8k_lag_setup_hash()`, `qca8k_lag_refresh_portmap()`, and the public join/leave callbacks.

## Control Flow

FDB operations serialize on `priv->reg_mutex`, write the ATU data registers, trigger an ATU function command, poll the busy bit, and optionally read back result status. Static FDB add/del use `QCA8K_FDB_LOAD` and `QCA8K_FDB_PURGE`; MDB add/del search for an existing entry, mutate the port mask, and reinsert or purge as needed. Dumps iterate with `QCA8K_FDB_NEXT` up to `QCA8K_NUM_FDB_RECORDS`.

VLAN operations similarly serialize on `reg_mutex`, issue VTU read/load/purge commands, update per-port egress mode bits in `QCA8K_REG_VTU_FUNC0`, and purge the VLAN when the last member is removed. PVID handling additionally updates egress VLAN and ingress CVID/SVID registers.

Bridge/STP logic maps Linux bridge states to hardware lookup states and toggles learning based on DSA port learning state. Membership updates connect a joining port to other ports in the same bridge unless both are isolated, update other ports' member masks, and finally update the joining/leaving port's mask to include the CPU port and eligible peers.

Mirroring first validates that the requested source is not already mirrored and that the single hardware monitor port is compatible. It sets the global mirror port and then either ingress mirror enable in lookup control or egress mirror enable in HOL control. Removal clears source bits and resets the monitor port to `0xF` when no mirror sources remain.

LAG join validates DSA LAG ID, max four members, hash TX type, and L2/L2+L3 hash mode. The hash selector is global, so different LAGs must share one hash mode unless only one LAG is configured. Portmap refresh updates trunk member and member-ID registers.

## State and Persistence

The file mutates `qca8k_priv` fields such as `port_enabled_map`, `port_isolated_map`, `mirror_rx`, `mirror_tx`, and `lag_hash_mode`. It also writes persistent hardware tables and registers: ATU/FDB, VTU/VLAN, port lookup membership, learning, STP state, EEE, MIB enablement, mirror selection, MTU, ageing, and LAG trunk tables. These settings persist until overwritten or switch reset. The common code relies on `reg_mutex` for table operations with command/busy registers.

## Dependencies and Integration Points

This code depends on DSA data structures, Linux bridge flags/states, switchdev VLAN/MDB objects, ethtool stat strings, regmap, and the definitions in `qca8k.h`. The DSA ops table in `qca8k-8xxx.c` exposes these functions to the kernel networking stack.

## Risks and Edge Cases

Several helpers return generic or unusual errors; for example ATU table-full in `qca8k_fdb_access()` returns `-1` rather than a specific errno. `qca8k_port_fdb_dump()` ignores the final `ret` and always returns 0, so callback errors may be hidden. `qca8k_port_mirror_del()` logs an error unconditionally through the `err:` label even when removal succeeds. MTU changes temporarily disable enabled CPU ports to avoid hardware panic; failures leave re-enable best-effort but should be tested. LAG member-ID update assumes an available slot and does not explicitly handle "no slot found" before programming index `i`.

## Test Signals

Signals include accurate ethtool stat names/counts for QCA832x and QCA833x, FDB add/delete/dump behavior with VID 0 defaulting to VID 1, MDB shared-port-mask behavior, VLAN add/delete/purge including last-member removal, PVID register updates, STP and learning transitions, isolated bridge ports not forwarding to each other, mirror add/delete enforcing one monitor port, MTU changes under traffic, ageing time quantization, and LAG offload rejection/acceptance for supported hash modes and member counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k-leds.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k-leds.c

## Purpose

This file implements optional LED class support for QCA8K switch port LEDs. It parses LED child nodes under DSA ports, maps each LED to the QCA8K LED control registers, registers `led_classdev` instances, supports direct brightness and hardware 4 Hz blink, and offloads Linux netdev LED trigger rules into switch LED rule bits.

## Important APIs, Types, and Functions

- `qca8k_phy_to_port()` maps internal PHY indices to DSA port numbers.
- `qca8k_get_enable_led_reg()` maps per-port/per-LED enable-pattern bits to the correct register and shift, accounting for special port 1/2/3 packing in `QCA8K_LED_CTRL3_REG`.
- `qca8k_get_control_led_reg()` maps rule-control fields for PHY0-3 and PHY4.
- `qca8k_parse_netdev()` converts Linux netdev trigger bits into QCA8K LED rule masks.
- `qca8k_led_brightness_set()` and `qca8k_led_brightness_get()` implement direct always-off/always-on control.
- `qca8k_cled_blink_set()` implements hardware blink only for 125 ms on/off, equivalent to 4 Hz.
- `qca8k_cled_hw_control_*()` implements LED trigger offload support, including status, supported-rules check, set/get, and associated netdevice lookup.
- `qca8k_parse_port_leds()` parses one port's `leds` node and registers LED class devices.
- `qca8k_setup_led_ctrl()` walks device-tree ports and initializes user-port LEDs.

## Control Flow

`qca8k_setup_led_ctrl()` looks for the top-level `ports` node. It skips CPU ports 0 and 6, reads each user port's `reg`, converts the DSA port number to an internal PHY LED index, and calls `qca8k_parse_port_leds()`. Per LED, the parser validates `reg` against the maximum of three LEDs per PHY, fills a `struct qca8k_led`, applies the default state (`on`, `keep`, or off), assigns LED class callbacks, builds a mandatory device name from the internal MDIO bus ID and port number, registers with `devm_led_classdev_register_ext()`, and frees the temporary name.

Brightness and blink callbacks update the pattern-enable bits. Hardware trigger offload first enables rule-controlled mode for that LED and then writes the trigger rule field. The get path verifies that the LED is in rule-controlled mode before translating hardware rule bits back into Linux trigger bits. The associated device callback maps the LED's PHY/port to the DSA user netdevice.

## State and Persistence

Per-LED runtime state is stored in `priv->ports_led[]`: port number, LED number, old rule placeholder, private pointer, and embedded `led_classdev`. Hardware LED mode/rule state is stored in QCA8K LED control registers and persists until reconfigured or reset. The code does not maintain a software shadow of rule fields beyond the LED classdev state.

## Dependencies and Integration Points

This file depends on `CONFIG_NET_DSA_QCA8K_LEDS_SUPPORT`, LED class APIs, LED default-state parsing, netdev trigger rule bits, fwnode/device property APIs, regmap, DSA port-to-netdev lookup, and constants/types from `qca8k.h` and `qca8k_leds.h`. It is included in the `qca8k` composite object only when Kconfig enables LED support.

## Risks and Edge Cases

The LED register layout is irregular; port 0/4 and ports 1-3 use different masks and shifts. Errors from `qca8k_get_enable_led_reg()` are ignored by callers that already expect valid port numbers, so invalid state would lead to bad register use. Hardware blink supports only 4 Hz; other delays intentionally fall back to software by returning `-EINVAL`. `qca8k_parse_netdev()` treats unknown nonzero rules as unsupported. Registration warnings do not abort setup for individual LED failures. The code assumes `priv->internal_mdio_bus` has been initialized before LED setup because it uses its ID in LED names.

## Test Signals

Test signals include LED class devices appearing for user ports with valid `leds` child nodes, no LED devices for CPU ports, default-state `on/off/keep` reflected in hardware, 125/125 blink offloaded to hardware, other blink rates falling back, netdev trigger offload for tx/rx/link/duplex bits, `hw_control_get_device` returning the user netdevice, and correct behavior for invalid LED `reg` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k-leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k.h

## Purpose

This header defines the QCA8K driver contract: register offsets, bit fields, constants, command enums, private data structures, LED descriptors, MIB/FDB structures, helper inline mappings, and prototypes shared by `qca8k-8xxx.c`, `qca8k-common.c`, and optional LED support.

## Important APIs, Types, and Functions

- Hardware constants define ports, CPU ports, max MTU, LAG capacity, PHY IDs, switch IDs, MIB counts, FDB size, and timeouts.
- Register and bitfield macros cover global control, port pad controls, PWS, MIB, MDIO master, LED control, MAC power, EEE, trunk/LAG, VLAN/ATU/VTU lookup, port lookup, queue/HOL, packet editing, L3, MIB, and MII MMD access.
- Command enums model FDB (`qca8k_fdb_cmd`), VLAN (`qca8k_vlan_cmd`), and MIB (`qca8k_mid_cmd`) operations.
- `struct qca8k_match_data` stores device ID, package flag, MIB count, and optional info ops.
- `struct qca8k_mgmt_eth_data` and `struct qca8k_mib_eth_data` store management Ethernet command/MIB completion state.
- `struct qca8k_ports_config` stores parsed RGMII/SGMII delay and clock settings.
- `struct qca8k_priv` is the central runtime state for switch ID/revision, mirror/LAG/port maps, regmap, buses, DSA switch, locks, reset GPIO, management conduit, MDIO cache, PCS instances, and LED array.
- Function prototypes expose common setup, register, DSA, FDB/MDB/VLAN, mirror, bridge, MTU, ageing, and LAG helpers.

## Control Flow

This header has no runtime control flow, but it encodes the interfaces used by the QCA8K implementation. The flow across source files is: `qca8k-8xxx.c` owns probe/setup/transport/phylink and calls common functions declared here; `qca8k-common.c` implements most DSA switch operations; `qca8k-leds.c` consumes LED constants and `struct qca8k_priv` LED storage; `qca8k_leds.h` conditionally declares the LED setup entry point.

## State and Persistence

The header defines both software state and persistent hardware state accessors. `struct qca8k_priv` fields such as enabled ports, isolation, mirror masks, LAG hash mode, MDIO page cache, management sequence number, and PCS/LED objects persist for the driver instance lifetime. Register macros define hardware state that persists until reset or reconfiguration.

## Dependencies and Integration Points

It depends on Linux delay, regmap, GPIO consumer, LED class, and QCA DSA tag header definitions. The prototypes are consumed by QCA8K compilation units and DSA operations. It also embeds assumptions about Linux bridge, switchdev, phylink, MDIO, ethtool, and netdevice APIs through function signatures and struct fields.

## Risks and Edge Cases

Macro correctness is critical because many fields are programmed with `FIELD_PREP`/`FIELD_GET`. The typo `QCA8K_LED_BLINK_FREQ_SHITF` is present but appears unused in the read files; if used later, the misspelling may propagate. `QCA8K_LED_COUNT` excludes CPU ports by deriving from total ports minus CPU ports. `qca8k_port_to_phy()` assumes ports 1-5 map to PHYs 0-4 and is invalid for CPU ports. Struct fields such as `port_enabled_map` and `port_isolated_map` are 8-bit, adequate for seven ports but fragile if reused for larger switches.

## Test Signals

Compile coverage is the main signal: all QCA8K objects should agree on prototypes and constants. Runtime signals include correct register addressing for all DSA operations, correct per-chip MIB count selection, successful internal PHY access using port-to-phy mapping, LED array indexing within bounds, and no sparse/compiler warnings for field width mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k_leds.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k_leds.h

## Purpose

This header provides the conditional interface for QCA8K LED setup. It allows the main QCA8K setup path to call `qca8k_setup_led_ctrl()` regardless of whether LED support is compiled in.

## Important APIs, Types, and Functions

- When `CONFIG_NET_DSA_QCA8K_LEDS_SUPPORT` is enabled, it declares `int qca8k_setup_led_ctrl(struct qca8k_priv *priv);`.
- Otherwise it defines a static inline stub returning 0.

## Control Flow

The header itself has no runtime control flow. At compile time it selects either the real LED setup function or the no-op fallback. `qca8k_setup()` can therefore call the function unconditionally and treat LED support as optional.

## State and Persistence

The header introduces no state. With LED support disabled, no LED class devices or LED hardware configuration are created by this interface.

## Dependencies and Integration Points

It depends on `struct qca8k_priv` being visible to callers through `qca8k.h`. The real implementation lives in `qca8k-leds.c`, included by the Makefile only when the same Kconfig symbol is enabled.

## Risks and Edge Cases

The Kconfig, Makefile, and header condition must remain aligned. If the C file is built without the declaration or the declaration exists without the object, build failures can result. The no-op stub makes systems without LED support silently skip LED initialization, which is expected but should be considered when diagnosing missing LED devices.

## Test Signals

Build QCA8K with LED support enabled and disabled. Enabled builds should link against `qca8k-leds.o`; disabled builds should compile with the inline stub and still probe switches successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/qca/qca8k_leds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/Kconfig

## Purpose

This Kconfig file defines build options for the Realtek DSA switch family, split into a common family menu, transport interface drivers (MDIO and SMI), chip drivers (RTL8365MB and RTL8366RB), and optional RTL8366RB LED support.

## Important APIs, Types, and Functions

- `NET_DSA_REALTEK` is the family-level tristate option and selects `FIXED_PHY`, `IRQ_DOMAIN`, `REALTEK_PHY`, and `REGMAP`.
- `NET_DSA_REALTEK_MDIO` and `NET_DSA_REALTEK_SMI` are bool interface options gated by OF support.
- `NET_DSA_REALTEK_RTL8365MB` depends on either interface and selects the `RTL8_4` DSA tagger.
- `NET_DSA_REALTEK_RTL8366RB` depends on either interface and selects the `RTL4_A` DSA tagger.
- `NET_DSA_REALTEK_RTL8366RB_LEDS` is a hidden bool defaulting to the RTL8366RB driver when LED class linkage permits.

## Control Flow

There is no runtime control flow. The dependency graph ensures that at least one transport interface can be enabled for chip drivers, and that chip drivers pull in the correct tag protocols.

## State and Persistence

State consists of kernel config selections persisted in `.config`. These selections determine which objects are built into `realtek_dsa.o`, `rtl8366.o`, and `rtl8365mb.o`.

## Dependencies and Integration Points

The options integrate with DSA, OF, regmap, IRQ domains, fixed PHY support, Realtek PHY support, tag protocol drivers, and LED class support. The menu help explicitly notes that a family driver needs both an interface driver and at least one chip subdriver to be useful.

## Risks and Edge Cases

Because MDIO/SMI are bools under a tristate family option, build combinations must be checked for built-in/module linkage with chip drivers. Chip drivers depend on an interface being configured but the interface alone cannot register a useful switch without a chip variant. LED support follows the RTL8366RB symbol by default and can be disabled indirectly by LED class constraints.

## Test Signals

Build matrix signals include Realtek family disabled, family enabled without chip drivers, MDIO-only, SMI-only, both interfaces, RTL8365MB and RTL8366RB as built-in/modules, and LED-compatible/incompatible configurations. Runtime signals are correct transport registration and tagger availability for selected chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/Makefile

## Purpose

This Makefile maps Realtek DSA Kconfig symbols to common, interface, and chip-specific objects.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_NET_DSA_REALTEK) += realtek_dsa.o`
- `realtek_dsa-objs := rtl83xx.o`, with `realtek-mdio.o` and/or `realtek-smi.o` appended when their interface configs are enabled.
- `obj-$(CONFIG_NET_DSA_REALTEK_RTL8366RB) += rtl8366.o`, composed from `rtl8366-core.o`, `rtl8366rb.o`, and optional `rtl8366rb-leds.o`.
- `obj-$(CONFIG_NET_DSA_REALTEK_RTL8365MB) += rtl8365mb.o`.

## Control Flow

There is no runtime flow. Kbuild assembles the common Realtek transport/core object and chip driver objects based on config selections.

## State and Persistence

The file controls build outputs only. It does not define runtime state.

## Dependencies and Integration Points

The object layout reflects the architecture: `rtl83xx.o` provides common interface-agnostic probe/register helpers, `realtek-mdio.o` and `realtek-smi.o` provide transports, and chip modules provide variants and DSA operations. Optional RTL8366RB LED code is conditionally folded into `rtl8366.o`.

## Risks and Edge Cases

Incorrect conditional inclusion can create missing transport symbols for chip drivers that call `realtek_mdio_driver_register()` or `realtek_smi_driver_register()`. Since `realtek_dsa.o` may include one or both transports, cross-config link coverage is important.

## Test Signals

Expected build outputs are `realtek_dsa.o` with the selected transport objects, `rtl8366.o` with optional LED object, and `rtl8365mb.o` when enabled. Link tests should cover MDIO-only, SMI-only, both, and no-chip configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-mdio.c

## Purpose

This file implements the MDIO transport adapter for Realtek DSA switches. It translates regmap-style 16-bit register reads/writes into the Realtek MDIO indirect-access sequence, delegates common device allocation and DSA registration to the `rtl83xx` core, and exports probe/remove/shutdown helpers for chip drivers that register MDIO devices.

## Important APIs, Types, and Functions

- `REALTEK_MDIO_*` constants define the MDIO indirect control, address, data, and operation registers.
- `realtek_mdio_write()` writes address operation, target register, data, and write command under `bus->mdio_lock`.
- `realtek_mdio_read()` writes address operation and target register, issues the read command, then reads the data register under the same lock.
- `realtek_mdio_info` is a `struct realtek_interface_info` with transport read/write callbacks.
- `realtek_mdio_probe()` calls `rtl83xx_probe()`, stores the parent bus and MDIO address in `realtek_priv`, sets `write_reg_noack`, and calls `rtl83xx_register_switch()`.
- `realtek_mdio_remove()` unregisters the switch then calls `rtl83xx_remove()`.
- `realtek_mdio_shutdown()` delegates to `rtl83xx_shutdown()`.

## Control Flow

Probe is intentionally thin. The common core creates and initializes `realtek_priv` and regmaps using `realtek_mdio_info`. The MDIO-specific code fills `priv->bus`, `priv->mdio_addr`, and `priv->write_reg_noack`. Successful probe ends with common switch registration.

Register writes use a four-step indirect sequence on the parent MDIO address: select address op in control0, write target register to address register, write value to data-write register, and trigger write op in control1. Reads use the same address setup, trigger read op, and read data-read register.

## State and Persistence

Runtime transport state is stored in `realtek_priv`: parent `mii_bus`, `mdio_addr`, and no-ack write function pointer. The underlying switch register state persists in hardware. The MDIO bus lock serializes indirect transactions so address/data/control sequences are not interleaved.

## Dependencies and Integration Points

The file depends on Linux MDIO, regmap, OF-capable device probing through chip drivers, and the common `rtl83xx` core. It exports symbols in the `REALTEK_DSA` namespace so chip modules can use the transport lifecycle helpers.

## Risks and Edge Cases

The indirect access sequence assumes all MDIO operations complete synchronously and does not poll a busy bit. Any bus error aborts the sequence and returns the error. `write_reg_noack` is the same as normal write for MDIO transport, unlike SMI where reset may not ACK. Correct locking is critical because concurrent transactions would corrupt the selected indirect address.

## Test Signals

Signals include successful probe over an MDIO-described Realtek switch, correct register reads/writes through regmap, no interleaving under concurrent DSA operations, clean unregister/remove, and exported namespace symbols resolving for chip drivers. Fault tests should simulate MDIO write/read failures at each step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-mdio.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-mdio.h

## Purpose

This header provides conditional wrappers and declarations for the Realtek MDIO transport driver, allowing chip drivers to compile regardless of whether MDIO interface support is enabled.

## Important APIs, Types, and Functions

- When `CONFIG_NET_DSA_REALTEK_MDIO` is enabled, `realtek_mdio_driver_register()` and `_unregister()` wrap `mdio_driver_register()` and `mdio_driver_unregister()`, and probe/remove/shutdown are declared.
- When disabled, registration is a no-op success, probe returns `-ENOENT`, and remove/shutdown are empty stubs.

## Control Flow

There is no runtime flow in the enabled case beyond inline wrapper calls. In disabled builds, chip-driver init can call the wrapper and continue without registering an MDIO driver.

## State and Persistence

No state is introduced. The enabled path affects global MDIO driver registration through the MDIO core; the disabled path does nothing.

## Dependencies and Integration Points

The header integrates chip drivers with the MDIO core and Kconfig-controlled transport availability. It expects `struct mdio_driver` and `struct mdio_device` declarations from included kernel headers in compilation units.

## Risks and Edge Cases

Returning success from disabled registration wrappers means callers must not interpret that as an MDIO transport being available. Probe's `-ENOENT` stub is useful if referenced directly, but normal disabled builds should not bind MDIO devices.

## Test Signals

Compile chip drivers with MDIO support enabled and disabled. Enabled builds should register and unregister an MDIO driver; disabled builds should link through stubs without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-mdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-smi.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-smi.c

## Purpose

This file implements the Realtek Simple Management Interface transport for DSA switches. SMI is a Realtek-specific bit-banged protocol using GPIO lines named like MDIO/MDC but not following the MDIO frame format. The file provides low-level start/stop, bit, byte, ACK, read/write operations, regmap transport callbacks, and exported probe/remove/shutdown helpers that integrate with the shared `rtl83xx` core.

## Important APIs, Types, and Functions

- `realtek_smi_clk_delay()` applies the variant-specific nanosecond delay.
- `realtek_smi_start()` and `realtek_smi_stop()` emit the protocol framing and switch GPIO direction/state.
- `realtek_smi_write_bits()` and `realtek_smi_read_bits()` shift data over GPIOs.
- `realtek_smi_wait_for_ack()`, `realtek_smi_write_byte()`, `realtek_smi_write_byte_noack()`, `realtek_smi_read_byte0()`, and `realtek_smi_read_byte1()` implement byte-level protocol and ACK/NACK behavior.
- `realtek_smi_read_reg()` and `realtek_smi_write_reg()` implement 16-bit register transactions under `priv->lock`.
- `realtek_smi_write_reg_noack()` supports reset writes where the chip naturally stops ACKing.
- `realtek_smi_info` provides regmap read/write callbacks to `rtl83xx_probe()`.
- `realtek_smi_probe()`, `realtek_smi_remove()`, and `realtek_smi_shutdown()` export lifecycle hooks for platform drivers.

## Control Flow

Probe calls `rtl83xx_probe()` with SMI regmap callbacks, obtains optional `mdc` and `mdio` GPIO descriptors as outputs, installs the no-ACK write callback, and registers the switch through `rtl83xx_register_switch()`. On failure after common probe, it calls `rtl83xx_remove()` to unwind.

An SMI read transaction takes `priv->lock` with IRQ save, emits start, writes the variant read command and low/high address bytes with ACK checks, reads low data byte with ACK and high data byte with final NACK, emits stop, releases the lock, and returns the 16-bit value. A write follows the same framing with variant write command, address bytes, low data byte, and high data byte with optional ACK suppression.

Remove gets drvdata, unregisters the DSA switch through the common core, and removes common resources. Shutdown delegates to `rtl83xx_shutdown()`.

## State and Persistence

Transport state is in `realtek_priv`: GPIO descriptors for MDC/MDIO, variant command bytes and clock delay, spinlock for command serialization, and no-ACK write pointer. Hardware register state persists on the switch until changed or reset. GPIO directions are driven during transactions and returned to input mode at stop.

## Dependencies and Integration Points

The file depends on GPIO consumer APIs, platform devices, regmap, spinlocks, delays, OF probing, and the common `rtl83xx` core. It exports symbols in the `REALTEK_DSA` namespace for chip platform drivers. It relies on `realtek_variant` fields (`cmd_read`, `cmd_write`, `clk_delay`) selected by the chip driver/core.

## Risks and Edge Cases

SMI timing is hardware-sensitive; too short a `clk_delay` or GPIO latency can cause ACK timeouts. The ACK retry count is fixed at 5. Optional GPIO acquisition can return NULL, but actual bit operations require valid descriptors, so board descriptions must provide working lines. Reset writes need no-ACK behavior or they may falsely fail. Because the transport uses a spinlock with IRQ save, the bit-banged transaction must remain short and non-sleeping aside from `ndelay`.

## Test Signals

Signals include successful platform probe with SMI GPIOs, correct chip detection through SMI regmap reads, successful register writes and reset no-ACK writes, no ACK timeouts under normal operation, DSA switch registration and traffic, clean remove/shutdown, and behavior under forced GPIO/ACK failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-smi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-smi.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-smi.h

## Purpose

This header provides conditional wrappers and declarations for the Realtek SMI platform transport driver, letting chip drivers compile whether or not SMI support is enabled.

## Important APIs, Types, and Functions

- With `CONFIG_NET_DSA_REALTEK_SMI` enabled, `realtek_smi_driver_register()` and `_unregister()` wrap platform driver registration, and probe/remove/shutdown are declared.
- With SMI disabled, registration is a no-op success, probe returns `-ENOENT`, and remove/shutdown are empty stubs.

## Control Flow

The enabled inline wrappers call the platform driver core. Disabled wrappers allow common chip-driver init/exit code to call transport registration functions without conditional compilation at each call site.

## State and Persistence

No state is stored by this header. Enabled wrappers affect global platform-driver registration; disabled wrappers have no runtime effect.

## Dependencies and Integration Points

It integrates chip drivers with the platform bus and Kconfig-controlled SMI availability. It expects `struct platform_driver` and `struct platform_device` to be visible in users.

## Risks and Edge Cases

Disabled registration returning 0 can make "no SMI transport registered" look like success to simple init code; this is intentional for multi-transport chip drivers but must be understood in diagnostics. Probe's `-ENOENT` stub should not be treated as a hardware probe failure in disabled builds.

## Test Signals

Compile chip drivers with SMI enabled and disabled. Enabled builds should register a platform driver and bind OF nodes; disabled builds should link through stubs and not expose an SMI transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-smi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek.h

## Purpose

This header defines shared Realtek DSA switch data structures, variant operations, common runtime state, VLAN/MIB helper structures, and exported helper prototypes used by the Realtek common core, transport drivers, and chip-specific drivers.

## Important APIs, Types, and Functions

- `REALTEK_HW_STOP_DELAY` and `REALTEK_HW_START_DELAY` define reset timing constants.
- `struct rtl8366_mib_counter` describes MIB counter layout for RTL8366-style helpers.
- `struct rtl8366_vlan_mc` and `struct rtl8366_vlan_4k` describe member-table and 4K VLAN entries.
- `struct realtek_priv` is the central driver state: device/reset/GPIOs, regmaps, locks, user and parent MDIO buses, MDIO address, variant pointer, embedded DSA switch, IRQ domain, LED-disable flag, CPU/port/VLAN/MIB metadata, operation vtable, no-ACK write hook, VLAN enable state, buffer, and per-chip private data.
- `struct realtek_ops` is the chip operation vtable for detect/reset/setup, MIB, VLAN member table, VLAN 4K table, MC index, VLAN enablement, port enablement, and PHY read/write.
- `struct realtek_variant` ties DSA ops, chip ops, phylink ops, SMI command/delay parameters, and chip-private allocation size together.
- Prototypes expose RTL8366 VLAN and ethtool-stat helper functions plus external variant instances `rtl8366rb_variant` and `rtl8365mb_variant`.

## Control Flow

The header has no direct control flow. It defines how control moves between layers: transport drivers provide regmap access and call common `rtl83xx` helpers; common/chip code stores state in `realtek_priv`; chip variants fill `realtek_variant` and `realtek_ops`; DSA callbacks use helper prototypes for VLAN and stats behavior.

## State and Persistence

`realtek_priv` holds all per-device state for the Realtek family, including both transport state (GPIOs, MDIO bus/address, regmaps) and switch state (CPU port, number of ports, VLAN enabled flags, IRQ domain, MIB counter metadata, chip data). Hardware state such as VLAN tables, port enablement, MIB counters, and PHY registers persists in the switch and is manipulated through the operation vtable.

## Dependencies and Integration Points

The header depends on Linux PHY, platform device, GPIO, DSA, and reset APIs. It is shared by MDIO and SMI transport files and chip drivers such as RTL8366RB and RTL8365MB. The external variants are integration points used by the common probe logic to bind compatible strings to chip-specific behavior.

## Risks and Edge Cases

Because `realtek_priv` embeds a `struct dsa_switch`, lifetime and drvdata setup must be consistent across transports and common code. The vtable contains many optional-looking operations but chip drivers must provide the operations used by their DSA callbacks. `buf[4096]` is a fixed scratch buffer that requires careful bounds discipline in users. State flags `vlan_enabled` and `vlan4k_enabled` must remain synchronized with hardware. Transport-specific fields are present in the shared struct, so chip code must not assume MDIO and SMI fields are always populated.

## Test Signals

Compile coverage across MDIO, SMI, RTL8366RB, and RTL8365MB validates type contracts. Runtime signals include successful common probe allocation, correct variant selection, DSA operations reaching chip ops, VLAN helper correctness, MIB stat reporting, PHY read/write through the selected transport, and clean shutdown/remove without stale IRQ domains or buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek.h -->
