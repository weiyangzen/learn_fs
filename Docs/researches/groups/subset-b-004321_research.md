# subset-b-004321 research

This grouped report covers the Microchip KSZ/LAN937x DSA common, DCB, PTP, SPI, and LAN937x interface files. Each section preserves the original source path so the reconciliation step can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_common.c

## Purpose
`ksz_common.c` is the shared DSA switch driver core for Microchip KSZ8xxx, KSZ9xxx, LAN937x, and LAN9646 switches. It identifies switch silicon, publishes chip capability tables, binds common DSA callbacks, coordinates setup and teardown, and delegates chip-specific register layouts and features through `struct ksz_dev_ops`.

## Important APIs, Types, and Functions
The exported entry points are `ksz_switch_alloc()`, `ksz_switch_register()`, `ksz_switch_remove()`, `ksz_switch_shutdown()`, `ksz_switch_suspend()`, and `ksz_switch_resume()`. Shared helper exports include `ksz_r_mib_stats64()`, `ksz88xx_r_mib_stats64()`, `ksz_port_stp_state_set()`, `ksz_get_gbit()`, `ksz_get_xmii()`, `ksz_switch_macaddr_get()`, `ksz_switch_macaddr_put()`, `ksz_handle_wake_reason()`, and the global `ksz_switch_chips[]` table.

The central integration object is `ksz_switch_ops`, a `struct dsa_switch_ops` table that wires DSA callbacks for tagging, setup, phylink, MDIO, VLAN/FDB/MDB, mirroring, STP, bridge flags, stats, MTU, WoL, PTP timestamping, flower offload, traffic control, EEE, and DCB. Silicon-specific behavior is selected by `ksz_switch_chips[]`, which binds each supported chip ID to register tables, masks, shifts, port capabilities, MIB layouts, PTP capability, TX queue count, and one of the device operation tables for KSZ8463, KSZ88xx, KSZ87xx, KSZ9477-like, or LAN937x devices.

## Control Flow
Probe-facing code starts with `ksz_switch_alloc()`, which allocates `dsa_switch` and `ksz_device`, then bus-specific code calls `ksz_switch_register()`. Registration toggles optional reset GPIOs, handles KSZ8463 strap pins, initializes mutexes, detects the chip with `ksz_switch_detect()`, validates it against platform data or OF match data, runs chip-specific `init()`, allocates per-port state and MIB counters, parses port interface/RGMII delay/fiber/synclko/WoL device-tree properties, then calls `dsa_register_switch()`. After DSA setup, MIB polling is scheduled.

DSA setup flows through `ksz_setup()`: allocate VLAN cache, reset hardware, parse drive strength properties, create PCS for SGMII-capable parts, configure broadcast and multicast storm controls, configure CPU port and STP multicast address handling, initialize MIB counters, run chip-specific setup, enable global/port/PTP IRQ domains if an IRQ exists, register the PTP clock when supported, register the user or side MDIO bus, initialize DCB, and finally set the hardware start bit. Error paths unwind PTP and IRQ state.

Runtime port control flows through DSA callbacks. STP changes update per-port TX/RX/learning bits and call `ksz_update_port_member()` to recompute forwarding masks based on bridge membership, STP forwarding state, isolation, CPU port, and HSR ports. VLAN/FDB/MDB/mirror operations are thin dispatchers into `dev_ops`. Phylink callbacks advertise capabilities from chip data, program xMII mode and RGMII delays on external MAC ports, set speed/duplex/flow control on link-up, and trigger immediate MIB reads on link-down.

## State and Persistence
The driver state is held in `struct ksz_device` and per-port `struct ksz_port`: chip identity, regmaps, device-tree flags, mutexes, IRQ domains, VLAN cache, MIB counters, bridge/STP flags, PTP state, WoL flags, HSR state, and an optional refcounted global switch MAC address. Hardware register state is volatile and restored by setup; there is no filesystem persistence. MIB values are accumulated in memory and periodically refreshed by delayed work to avoid hardware counter overflow. WoL state can intentionally survive shutdown by avoiding reset when a port has PME enabled.

## Dependencies and Integration Points
The file integrates with Linux DSA, phylink, phylib/MDIO, regmap, OF, GPIO, pinctrl, irqdomain, ethtool stats/WoL/EEE, switchdev bridge/VLAN/FDB/MDB, tc flower/CBS/ETS, HSR offload, PTP hooks from `ksz_ptp.h`, DCB hooks from `ksz_dcb.h`, and chip-specific modules `ksz8`, `ksz9477`, and `lan937x`. Bus drivers such as `ksz_spi.c` provide regmaps and call the exported lifecycle functions.

## Risks and Edge Cases
Chip tables are dense and easy to regress: wrong port counts, CPU masks, register maps, MIB layouts, or interface capability arrays can break probe or expose invalid ports. `ksz_switch_detect()` has family-specific ID logic, including KSZ9893 SKU differentiation and LAN9646 special handling. MDIO setup validates `phy-handle` parents and PHY addresses; mismatched DT fails registration. IRQ setup nests global, port, PHY, and optional PTP domains and has multiple unwind points. Traffic-control code rejects unsupported ETS weights and requires all queues to be covered. WoL and HSR share a single global switch MAC address, so MAC changes are blocked while those features own it. `ksz_switch_macaddr_put()` assumes a valid refcounted address exists when called.

## Test Signals
Useful signals include successful probe for every compatible in `ksz_switch_chips[]`, DSA registration and teardown without leaks, correct tag protocol selection, MDIO child bus registration and IRQ mapping, STP forwarding/isolation behavior, VLAN/FDB/MDB/mirror operations, MIB counter rollover avoidance, phylink mode and RGMII delay programming, EEE advertisement only on allowed internal PHYs, CBS/ETS qdisc offload acceptance and rejection, WoL PME wake reason logging, HSR join/leave constraints, suspend/resume MIB work handling, and shutdown behavior with and without active WoL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_common.h

## Purpose
`ksz_common.h` is the shared private contract for the Microchip KSZ DSA driver family. It defines the device, port, chip capability, IRQ, MIB, ALU, and operation-table structures used by common code, bus drivers, and chip-specific implementations, plus the register helper API for 8/16/32-bit regmaps.

## Important APIs, Types, and Functions
Major data types include `struct ksz_chip_data`, `struct ksz_device`, `struct ksz_port`, `struct ksz_dev_ops`, `struct ksz_irq`, `struct ksz_ptp_irq`, `struct ksz_port_mib`, `struct vlan_table`, and `struct alu_struct`. Enumerations model supported chips (`enum ksz_model`), abstract register slots (`enum ksz_regs`), mask slots, shift slots, and xMII bit encodings.

The header declares the common lifecycle exports, MIB/stat helpers, STP helper, xMII helpers, switch MAC address helpers, wake-reason helper, and `ksz_switch_chips[]`. Inline helpers wrap `regmap_read()`, `regmap_write()`, and `regmap_update_bits()` for global and per-port register access, and encode model-family predicates such as `is_ksz8()`, `is_ksz9477()`, `is_lan937x()`, and `ksz_is_sgmii_port()`.

## Control Flow
This header does not execute by itself, but it shapes the driver flow. Bus drivers allocate `ksz_device`, initialize three regmaps, and call `ksz_switch_register()`. Common code then consults `ksz_chip_data` and calls hooks in `ksz_dev_ops` for reset, setup, port address calculation, PHY access, VLAN/FDB/MDB operations, MIB reads, MTU changes, PME register access, PCS creation, and chip-specific teardown.

## State and Persistence
All persistent runtime state is in memory and hardware registers referenced by these structures. `ksz_device` owns global switch state and synchronization primitives; each `ksz_port` owns per-port link, STP, learning, interface, RGMII delay, MIB, IRQ, PTP, and flow-control state. No disk persistence is defined. Regmap caching is explicitly disabled in the generated SPI regmap configs.

## Dependencies and Integration Points
The header depends on Linux networking and driver subsystems: DSA, phylink, PCS XPCS, PHY, regmap, IRQ, mutexes, platform data, and optional PTP declarations from `ksz_ptp.h`. It is consumed by `ksz_common.c`, bus access drivers such as `ksz_spi.c`, DCB/PTP files, and chip-specific KSZ8/KSZ9477/LAN937x modules.

## Risks and Edge Cases
The abstract register arrays must stay aligned with `enum ksz_regs`, masks, and shifts; missing entries can cause common code to write the wrong hardware address. Inline read helpers assign output values even when regmap reads fail, so callers must respect return codes. Per-port helpers depend on a correct `get_port_addr()` implementation. Family predicates drive large feature decisions and must be updated with any new chip IDs. The regmap macro parameters encode SPI command endianness, address width, padding, and alignment, making bus access fragile if reused incorrectly.

## Test Signals
Compile coverage should include PTP enabled and disabled configurations, all bus drivers using the regmap macros, and chip-specific modules consuming `ksz_dev_ops`. Runtime signals include correct register addresses from per-port helpers, expected chip-family predicate behavior, clean locking through custom regmap lock/unlock callbacks, and successful probe on chips with SGMII, side MDIO, PTP, and WoL capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_dcb.c

## Purpose
`ksz_dcb.c` implements DSA DCB priority controls for KSZ switches. It manages default port priority, global DSCP-to-internal-priority mapping, and apptrust selector configuration for PCP and DSCP priority sources across KSZ8 and KSZ9477-like register layouts.

## Important APIs, Types, and Functions
Public functions are `ksz_port_get_default_prio()`, `ksz_port_set_default_prio()`, `ksz_port_get_dscp_prio()`, `ksz_port_add_dscp_prio()`, `ksz_port_del_dscp_prio()`, `ksz_port_set_apptrust()`, `ksz_port_get_apptrust()`, `ksz_dcb_init_port()`, and `ksz_dcb_init()`. Internal helpers select family-specific registers (`ksz_get_default_port_prio_reg()`, `ksz_get_dscp_prio_reg()`, `ksz_get_apptrust_map_and_reg()`), initialize DSCP maps, and validate apptrust order.

## Control Flow
Global setup calls `ksz_dcb_init()`, which initializes every DSCP entry to a deterministic mapping and enables DSCP remapping on non-KSZ8 parts. Per-port setup calls `ksz_dcb_init_port()`, which sets Best Effort as the default priority and sets default apptrust to PCP. User DCB calls then read or update the relevant port or global registers through common `ksz_*` helpers. DSCP add writes a global table entry; DSCP delete restores that DSCP to Best Effort when the current entry matches the requested priority.

## State and Persistence
State is hardware-register backed: default priority bits live in per-port control registers; DSCP maps live in global TOS/DSCP registers; apptrust state lives in per-port priority-source enable bits. No software cache persists the DCB map, and no disk state exists. The DSA flag `dscp_prio_mapping_is_global` in common setup matches the global DSCP table behavior here.

## Dependencies and Integration Points
The file depends on DSA DCB callbacks, `net/dscp.h`, `net/ieee8021q.h`, common KSZ helpers, and KSZ8 family predicates. It is integrated into `ksz_switch_ops` through DSA callbacks and is initialized from `ksz_common.c` setup and port setup paths.

## Risks and Edge Cases
Register packing differs: KSZ8-style chips map four DSCP values per byte with two-bit priorities, while KSZ9477-style chips map two DSCP values per byte with three-bit priorities. Non-KSZ8 DSCP remapping must be enabled or the hardware falls back to DSCP bits 3-5. Apptrust order is fixed by hardware, and validation rejects reordered or unsupported selector lists. `ksz_init_global_dscp_map()` writes all DSCP entries but only returns the last write result, so an intermediate failure would be overwritten by later success.

## Test Signals
Test by reading default priority after init, setting boundary priorities around `num_ipms`, validating all 64 DSCP entries, toggling DSCP remap on KSZ9477-like parts, checking KSZ8 queue conversion, verifying apptrust accepts empty/PCP/DSCP/PCP+DSCP in fixed order and rejects reversed order, and confirming DSA DCB callbacks surface expected `-EINVAL`, `-ERANGE`, or register errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_dcb.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_dcb.h

## Purpose
`ksz_dcb.h` declares the DCB support functions used by the KSZ common DSA driver. It exposes per-port priority and apptrust operations plus global and per-port initialization hooks.

## Important APIs, Types, and Functions
The header declares DSA-facing callbacks for default priority, DSCP priority add/delete/get, apptrust set/get, `ksz_dcb_init_port()`, and `ksz_dcb_init()`. It includes `net/dsa.h` and `ksz_common.h` so functions can operate on `struct dsa_switch` and `struct ksz_device`.

## Control Flow
There is no local control flow. `ksz_common.c` installs these functions into `ksz_switch_ops` and calls the init helpers during switch setup and user-port setup.

## State and Persistence
The header defines no state. State is managed by `ksz_dcb.c` through hardware registers selected from `struct ksz_device` chip data.

## Dependencies and Integration Points
This is the coupling point between the common driver and the DCB implementation. Any build unit using these declarations needs the KSZ private structures and DSA definitions.

## Risks and Edge Cases
Because the prototypes are unconditional, build configurations must compile `ksz_dcb.c` whenever `ksz_common.c` references DCB callbacks. Signature drift would break DSA ops initialization at compile time.

## Test Signals
Compile with the Microchip KSZ DSA driver enabled and confirm `ksz_switch_ops` resolves all DCB symbols. Runtime DCB behavior should be validated through the implementation file's test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_dcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_ptp.c

## Purpose
`ksz_ptp.c` implements hardware timestamping and PTP hardware clock support for PTP-capable KSZ/LAN937x switches. It registers a PHC, controls clock read/set/adjust operations, handles per-output triggers, enables switch timestamp mode, reconstructs partial RX/TX timestamps, and builds nested IRQ domains for transmit timestamp events.

## Important APIs, Types, and Functions
Public functions are `ksz_ptp_clock_register()`, `ksz_ptp_clock_unregister()`, `ksz_get_ts_info()`, `ksz_hwtstamp_get()`, `ksz_hwtstamp_set()`, `ksz_port_txtstamp()`, `ksz_port_deferred_xmit()`, `ksz_port_rxtstamp()`, `ksz_ptp_irq_setup()`, and `ksz_ptp_irq_free()`. PTP clock callbacks include `ksz_ptp_gettime()`, `ksz_ptp_settime()`, `ksz_ptp_adjfine()`, `ksz_ptp_adjtime()`, `ksz_ptp_enable()`, `ksz_ptp_verify_pin()`, and `ksz_ptp_do_aux_work()`. Timestamp IRQ handling is split between a per-port PTP IRQ domain and per-message nested IRQ handlers for Sync, PDelay_Req, and PDelay_Resp.

## Control Flow
Clock registration initializes locks and `ptp_clock_info`, starts the hardware clock, configures P2P transparent-clock behavior, creates pin descriptors, and registers the PHC. `ksz_hwtstamp_set()` validates requested TX/RX modes, updates per-port enable flags and message IRQ enables, sets or clears one-step mode, then calls `ksz_ptp_enable_mode()` to enable PTP tagging and the PTP message parser only when at least one port needs timestamping.

TX timestamping classifies outgoing packets. For one-step P2P, Sync is handled in hardware and PDelay_Resp correction can be updated through the tagger path. For two-step timestampable messages, `ksz_port_txtstamp()` clones the skb and stores it in the KSZ skb control block. `ksz_port_deferred_xmit()` queues the real skb through DSA, waits for a completion triggered by the timestamp IRQ, and completes the clone's TX timestamp. RX timestamping reconstructs full time from the partial timestamp in the tagger metadata and, for one-step P2P PDelay_Req, subtracts the partial ingress timestamp from the correction field.

Clock adjustment paths serialize on `ptp_data.lock`. `settime()` writes shadow time registers and loads the clock; `adjfine()` computes subnanosecond rate correction; `adjtime()` performs hardware step adjustment. If a periodic output is running, set/adjust operations restart it at the next safe event. Auxiliary work refreshes `ptp_data.clock_time` once per second so partial timestamps can be reconstructed around the correct four-second window.

## State and Persistence
PTP state lives in `struct ksz_ptp_data` and per-port PTP fields in `struct ksz_port`: clock pointer, capabilities, pin descriptors, mutex/spinlock, cached clock time, TOU mode, periodic output target/period, hardware timestamp config, TX/RX enable flags, per-message IRQ descriptors, last TX timestamp, and completion. State is volatile and reinitialized on setup; no disk persistence exists. The cached clock time is a software aid for reconstructing partial hardware timestamps.

## Dependencies and Integration Points
The implementation depends on Linux PTP clock APIs, DSA tagger data (`ksz_tagger_data()` and `KSZ_SKB_CB()`), `ptp_classify_raw()`, `ptp_parse_header()`, timestamp completion helpers, irqdomain, common KSZ regmap helpers, and register definitions from `ksz_ptp_reg.h`. `ksz_common.c` calls clock and IRQ setup only for chip data marked `ptp_capable`.

## Risks and Edge Cases
The hardware clock seconds field is 32-bit and trigger target seconds are validated accordingly. Partial timestamp reconstruction depends on the auxiliary worker running often enough and can be wrong if `clock_time` is stale by more than two seconds. `ksz_ptp_tou_reset()` overwrites `ret` after setting `TRIG_RESET`, so an initial reset write failure can be lost if later writes succeed. TX timestamp wait timeout silently drops the timestamp. `HWTSTAMP_TX_ON` is LAN937x-only; other chips support one-step P2P mode. Nested IRQ mask semantics are inverted relative to common IRQ code because the PTP TX interrupt-enable register uses set bits to enable sources.

## Test Signals
Validate `ethtool -T` reports a PHC index and expected modes, `SIOCSHWTSTAMP` accepts supported filters and rejects unsupported TX types, PTP clock get/set/adjfine/adjtime operations, RX timestamp reconstruction across four-second rollover, TX timestamp completion for Sync/PDelay messages, one-step P2P correction updates, perout start/stop with duty-cycle validation, LAN937x GPIO output routing, IRQ mask/unmask behavior, and cleanup through clock unregister and `ksz_ptp_irq_free()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_ptp.h

## Purpose
`ksz_ptp.h` declares the optional PTP and hardware timestamping interface for the KSZ DSA driver. It provides the real data structure and function prototypes when `CONFIG_NET_DSA_MICROCHIP_KSZ_PTP` is enabled, and no-op or NULL stubs when it is disabled.

## Important APIs, Types, and Functions
With PTP enabled, the header defines `KSZ_PTP_N_GPIO`, `enum ksz_ptp_tou_mode`, and `struct ksz_ptp_data` containing `ptp_clock_info`, the registered `ptp_clock`, two pin descriptors, locks, cached clock time, TOU mode, and periodic-output state. It declares PHC registration, timestamp info, hwtstamp get/set, TX/RX timestamp hooks, deferred transmit, and IRQ setup/free functions.

## Control Flow
The header controls compile-time integration. `ksz_common.c` can unconditionally name the PTP callbacks in `ksz_switch_ops`; when PTP support is disabled, callbacks that DSA should omit are defined as `NULL`, while setup/free routines compile to success/no-op stubs.

## State and Persistence
When enabled, PTP state is embedded in `struct ksz_device` through this header. When disabled, only a mutex-containing placeholder `struct ksz_ptp_data` remains so common structures still compile. No persistence is provided here.

## Dependencies and Integration Points
The enabled path depends on `linux/ptp_clock_kernel.h`, DSA switch objects, hwtstamp config types, skb types, and kthread work. It is included by `ksz_common.h` so the common device structure can embed PTP data.

## Risks and Edge Cases
The disabled build path replaces function identifiers with `NULL` macros for DSA callbacks, so callers outside DSA setup must avoid invoking those macros as functions. Structure layout differs substantially between enabled and disabled configurations, which makes conditional compilation boundaries important.

## Test Signals
Build both PTP-enabled and PTP-disabled kernels. In the disabled build, probe should not attempt PHC registration and DSA timestamp callbacks should be absent. In the enabled build, all prototypes should resolve to `ksz_ptp.c` and the runtime tests from that implementation should pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_ptp_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_ptp_reg.h

## Purpose
`ksz_ptp_reg.h` defines PTP, trigger output, timestamp, interrupt, and LAN937x GPIO/LED register offsets and bit fields used by `ksz_ptp.c`.

## Important APIs, Types, and Functions
The file is macro-only. It defines global LED override/source registers, PTP clock control bits (`PTP_READ_TIME`, `PTP_LOAD_TIME`, `PTP_CLK_ADJ_ENABLE`, `PTP_CLK_ENABLE`, and related fields), subnanosecond rate masks, PTP message configuration bits, unit index fields, trigger status/interrupt/control fields, trigger timing registers, and per-port timestamp/interrupt registers. Message index constants map PDelay_Resp, PDelay_Req, and Sync to the three timestamp IRQ slots.

## Control Flow
There is no executable control flow. `ksz_ptp.c` composes these masks with common regmap helpers to select GPIOs, reset trigger units, configure periodic outputs, read/write PHC time, enable PTP packet parsing, and decode/clear timestamp interrupts.

## State and Persistence
These macros name volatile hardware state. Persistence and caching are handled by the PTP implementation and the switch hardware, not by this header.

## Dependencies and Integration Points
The header assumes Linux bit macros such as `BIT()` and `GENMASK()` are already available through including translation units. It is tightly coupled to `ksz_ptp.c` and the abstract PTP register slots in `ksz_common.h`/chip data.

## Risks and Edge Cases
Incorrect bit definitions can misroute LAN937x LED pins, enable the wrong trigger unit, clear the wrong W1C interrupt bit, or break timestamp message selection. Some field names represent bit masks while message constants represent logical array indexes, so mixing them would be hazardous.

## Test Signals
PTP clock control, periodic output, GPIO routing, and TX timestamp IRQ tests provide the runtime validation for these definitions. Register traces should show writes to the documented offsets and W1C clearing of `REG_PTP_PORT_TX_INT_STATUS__2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_ptp_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_spi.c

## Purpose
`ksz_spi.c` is the SPI bus glue for Microchip KSZ/LAN937x DSA switches. It creates width-specific regmaps over SPI, handles KSZ8463's nonstandard SPI command encoding, matches OF/SPI IDs to chip data, and invokes the common switch lifecycle.

## Important APIs, Types, and Functions
The module defines regmap tables with `KSZ_REGMAP_TABLE()` for KSZ8795, KSZ8863/88x3, and KSZ9477-like protocols, and `KSZ8463_REGMAP_TABLE()` with custom `ksz8463_spi_read()` and `ksz8463_spi_write()` callbacks. The driver entry points are `ksz_spi_probe()`, `ksz_spi_remove()`, and `ksz_spi_shutdown()`. OF match data points to entries in `ksz_switch_chips[]` for KSZ8463, KSZ87xx, KSZ88xx, KSZ9xxx, LAN937x, and LAN9646.

## Control Flow
On probe, the driver allocates a `ksz_device`, retrieves match data, stores the expected chip ID for special initialization, chooses the regmap config family, initializes the 8/16/32-bit regmaps with the shared regmap mutex and chip access tables, copies optional platform data, configures SPI mode 3, records the SPI IRQ, and calls `ksz_switch_register()`. Remove calls `ksz_switch_remove()`. Shutdown calls `ksz_switch_shutdown()` and clears driver data.

## State and Persistence
State consists of the SPI device, the allocated `ksz_device`, three regmaps, optional platform data, and the IRQ number. No disk state exists. Register caching is disabled; all access goes to hardware. The KSZ8463 read/write helpers perform endian conversion on big-endian hosts.

## Dependencies and Integration Points
The file depends on Linux SPI, regmap, module infrastructure, unaligned access helpers, OF match tables, and the common KSZ driver API. It exports no symbols; integration is through `module_spi_driver()` and common lifecycle calls.

## Risks and Edge Cases
Choosing the wrong regmap config breaks every register access. KSZ8463 command encoding depends on access width and address alignment and is easy to regress. The SPI ID table names do not carry driver data, so non-OF users rely on platform data and detection. Probe sets `spi->mode` and calls `spi_setup()` after regmaps are initialized, so controller mode assumptions should be tested. Regmap access tables from chip data restrict valid addresses on some chips.

## Test Signals
Probe each compatible over SPI, verify 8/16/32-bit register reads and writes, exercise KSZ8463 byte/word/dword accesses and big-endian conversions, confirm SPI mode 3 is accepted by controllers, validate IRQ propagation into common setup, test remove/shutdown paths, and check module alias matching for `spi:lan937x` and listed device IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/lan937x.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/lan937x.h

## Purpose
`lan937x.h` declares the LAN937x chip-specific operations consumed by the common KSZ driver. These functions implement LAN937x reset, setup, port configuration, side MDIO, PHY access, MTU, phylink capability, RGMII delay, ageing, and CBS credit increment behavior.

## Important APIs, Types, and Functions
The header declares `lan937x_reset_switch()`, `lan937x_setup()`, `lan937x_teardown()`, `lan937x_port_setup()`, `lan937x_config_cpu_port()`, `lan937x_switch_init()`, `lan937x_switch_exit()`, `lan937x_mdio_bus_preinit()`, `lan937x_create_phy_addr_map()`, `lan937x_r_phy()`, `lan937x_w_phy()`, `lan937x_change_mtu()`, `lan937x_phylink_get_caps()`, `lan937x_setup_rgmii_delay()`, `lan937x_set_ageing_time()`, and `lan937x_tc_cbs_set_cinc()`.

## Control Flow
There is no local control flow. `ksz_common.c` assigns these functions into `lan937x_dev_ops`, and then common DSA setup invokes them through `struct ksz_dev_ops` at lifecycle and feature-specific points.

## State and Persistence
The header defines no state. LAN937x runtime state is held in `struct ksz_device`, per-port structures, and LAN937x hardware registers managed by the implementation file outside this subset.

## Dependencies and Integration Points
This header is included by `ksz_common.c`. Its prototypes depend on `struct ksz_device`, `struct dsa_switch`, and `struct phylink_config` declarations supplied by the including context and KSZ common headers.

## Risks and Edge Cases
Prototype drift between this header, the LAN937x implementation, and `lan937x_dev_ops` will break builds or feature dispatch. Side MDIO functions are only meaningful for chip data with `phy_side_mdio_supported`; mismatched capability wiring would fail MDIO setup in common code.

## Test Signals
Compile LAN937x-enabled builds and probe LAN9370/1/2/3/4 devices. Runtime signals include successful side-MDIO preinit and PHY address mapping, correct CPU port setup, LAN937x-specific phylink capabilities and RGMII delays, MTU changes, ageing timer programming, and CBS offload through `lan937x_tc_cbs_set_cinc()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/lan937x.h -->
