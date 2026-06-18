# Research: subset-b-004328

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8365mb.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8365mb.c

Purpose: this is the Realtek RTL8365MB-family DSA subdriver for switches managed through the common Realtek SMI/MDIO transport. It supports RTL8365MB-VC plus related RTL8367S and RTL8367RB-VB IDs, programs vendor jam tables, exposes internal PHYs over a user MDIO bus, configures CPU tagging, controls RGMII external ports, demultiplexes link-change interrupts, and exports hardware MIB counters through ethtool and stats64.

Important APIs, types, and functions: `struct rtl8365mb_chip_info` describes supported chip IDs, external interface mappings, and per-chip jam tables. `struct rtl8365mb` stores chip info, CPU tag settings, interrupt state, a MIB mutex, and per-port `rtl8365mb_port` stats/work state. PHY access goes through `rtl8365mb_phy_ocp_read()`, `rtl8365mb_phy_ocp_write()`, `rtl8365mb_phy_read()`, and `rtl8365mb_phy_write()` using the indirect OCP register window under `rtl83xx_lock()`. DSA/phylink entry points include `rtl8365mb_setup()`, `rtl8365mb_teardown()`, `rtl8365mb_phylink_get_caps()`, `rtl8365mb_phylink_mac_config()`, link up/down callbacks, MTU/STP/stat callbacks, and `rtl8365mb_change_tag_protocol()`. The exported variant is `rtl8365mb_variant`, consumed by `realtek_smi_probe()` and `realtek_mdio_probe()`.

Control flow: detection writes the magic register, reads chip ID/version, selects a `chip_info`, sets default CPU tag format/position, and declares the maximum port count. DSA setup hardware-resets the switch, applies chip-specific and common jam tables, optionally creates a nested IRQ domain from the `interrupt-controller` child node, builds the CPU-port mask from DSA CPU ports, programs CPU tag insertion, initializes every non-unused port to forward only to the CPU, disables learning, sets STP disabled, initializes per-port private state, configures default MTU, registers the internal user MDIO bus, and initializes delayed stats work. Phylink config only implements RGMII external interfaces: it parses optional `tx-internal-delay-ps` and `rx-internal-delay-ps`, writes RGMII delay and interface-select registers, then link-up forces link/speed/duplex/pause bits while link-down clears forced mode.

State and persistence: persistent driver state is in `priv->chip_data`: selected chip info, CPU tag configuration, the parent IRQ number, per-port delayed work, and cached rtnl stats. Hardware state includes jam-table registers, indirect PHY OCP address prefix, external interface mode/delay/force registers, CPU tag registers, port isolation, per-port learn limits, MSTP state, global maximum frame size, interrupt polarity/status/control registers, and MIB address/counter registers. MIB stats64 data is periodically refreshed by delayed work because the DSA `get_stats64` callback cannot sleep; ethtool counter reads use the blocking MIB path directly under `mib_lock`. Teardown cancels stats work and tears down IRQ resources.

Dependencies and integration points: this file depends on `realtek.h`, `realtek-smi.h`, `realtek-mdio.h`, and common `rtl83xx` helpers for regmap locking, reset handling, DSA registration, and internal MDIO. It integrates with DSA switch ops, phylink MAC ops, irqdomain nested interrupts, OF interrupt and port properties, bridge/STP state, VLAN-sized MTU accounting, ethtool IEEE stats groups, and Realtek tag protocols `RTL8_4` and `RTL8_4T`.

Risks: only RGMII is implemented despite wider hardware mode definitions, so DT requesting MII/RMII/SGMII-style modes will not be configured. Interrupt setup treats missing or failed IRQ setup as non-fatal except probe deferral, reducing link-change notification quality. The MIB read path is register-sequence sensitive and shared, so missing locking would corrupt reads; stats64 intentionally lags by the polling interval. CPU tag protocol changes modify hardware tag position and format at runtime, so mismatched DSA taggers break traffic. Jam-table values are vendor-derived and sparse, making new chip revisions risky without hardware validation.

Test signals: useful checks are probe detection logs for the expected chip, successful DSA registration through both SMI and MDIO transports, working internal PHY MDIO reads/writes, RGMII fixed-link traffic with requested delays, correct Realtek tag protocol selection and runtime protocol changes, link-change IRQ propagation to PHY child IRQs, bridge STP state blocking/forwarding behavior, max-MTU register changes through CPU port MTU updates, delayed stats64 growth under traffic, and clean teardown without pending work or IRQ mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8365mb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366-core.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366-core.c

Purpose: this file is a shared helper library for RTL8366-family Realtek DSA drivers. It implements VLAN member-configuration allocation, PVID programming, VLAN 4K enable/disable sequencing, VLAN add/delete DSA callbacks, and generic ethtool MIB statistic plumbing through chip-specific `realtek_ops`.

Important APIs, types, and functions: exported helpers include `rtl8366_mc_is_used()`, `rtl8366_set_vlan()`, `rtl8366_set_pvid()`, `rtl8366_enable_vlan4k()`, `rtl8366_enable_vlan()`, `rtl8366_reset_vlan()`, `rtl8366_vlan_add()`, `rtl8366_vlan_del()`, `rtl8366_get_strings()`, `rtl8366_get_sset_count()`, and `rtl8366_get_ethtool_stats()`. The key internal routine is `rtl8366_obtain_mc()`, which finds, creates, or recycles a VLAN member configuration (`struct rtl8366_vlan_mc`) for a VID using the chip-specific 4K VLAN table.

Control flow: VLAN addition validates the VID through `priv->ops->is_vlan_valid()`, enables VLAN 4K mode, builds member and untag bitmaps from the DSA port and bridge flags, updates the 4K VLAN table, obtains a member-config slot, commits updated member/untag/FID fields, and optionally programs the port PVID by setting the member-config index. VLAN deletion scans member-config slots for the VID, removes the port from member and untag masks, and clears the slot if no ports remain. Reset disables VLAN and VLAN 4K mode and clears all configured member slots.

State and persistence: the helper updates `priv->vlan_enabled` and `priv->vlan4k_enabled` as software mirrors of hardware VLAN mode. Persistent forwarding state lives in chip-specific VLAN 4K and member-config hardware tables and per-port MC index registers accessed through `priv->ops`. Ettool stats are not cached here; the helper reads each chip-provided MIB counter on demand.

Dependencies and integration points: this file depends on `struct realtek_priv`, `realtek_ops` VLAN methods, DSA switch callbacks, bridge VLAN flags, and the shared `rtl8366_vlan_mc`, `rtl8366_vlan_4k`, and `rtl8366_mib_counter` structures declared in Realtek common headers. It is consumed by RTL8366RB and similar drivers that supply hardware-specific VLAN and MIB backends.

Risks: the member-config table is small and can become full; recycling only chooses entries not referenced by any port PVID. Deleting a VLAN only updates the member-config table, not the 4K table contents, so stale 4K state may persist until reused. `rtl8366_get_sset_count()` returns zero rather than `-EOPNOTSUPP` for unsupported sets, which differs from many ethtool implementations. VLAN 4K enablement is forced from `rtl8366_vlan_add()` because ordinary VLAN enablement alone is noted as inconclusive.

Test signals: add/delete VLANs with tagged, untagged, and PVID flags; exhaust and recycle member-config entries; verify `priv->vlan_enabled`/`vlan4k_enabled` after enable/disable/reset; inspect per-port PVID MC indices; validate ethtool string/count/counter output through a concrete driver such as RTL8366RB; and test error propagation from chip-specific ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366rb-leds.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366rb-leds.c

Purpose: this optional companion adds Linux LED class support for RTL8366RB per-port LED groups. It parses `leds` child nodes under DSA port nodes, maps each LED group's manual-control bit in the RTL8366RB LED registers, and registers binary LED class devices with blocking brightness setters.

Important APIs, types, and functions: `rtl8366rb_setup_leds()` iterates DSA ports and their LED child nodes. `rtl8366rb_setup_led()` parses each LED node's `reg` LED group, initializes a `struct rtl8366rb_led`, applies `default-state`, and calls `devm_led_classdev_register_ext()`. `rb8366rb_set_port_led()` updates group/port bits and switches the group mode to `RTL8366RB_LEDGROUP_FORCE` through `rb8366rb_set_ledgroup_mode()`. `rb8366rb_get_port_led()` reads the manual LED state.

Control flow: setup skips ports with no DT node or no `leds` child. For each child LED, `reg` selects one of four LED groups; invalid groups fail setup. Default state `on` or `off` immediately writes the manual state, while `keep` reads the current bit. The registered brightness callback writes manual on/off state and ensures the group is in force mode, because the manual state registers are ignored when a hardware trigger mode is selected.

State and persistence: software state lives in `struct rtl8366rb_led leds[port][group]` embedded in the chip private structure when `CONFIG_NET_DSA_REALTEK_RTL8366RB_LEDS` is enabled. Hardware state is split between group trigger mode in `RTL8366RB_LED_CTRL_REG` and per-port manual bits in `RTL8366RB_LED_0_1_CTRL_REG` or `RTL8366RB_LED_2_3_CTRL_REG`. Device-managed LED registration handles cleanup.

Dependencies and integration points: this file depends on `rtl8366rb.h`, the parent Realtek regmap, DSA port device nodes, firmware node LED properties, and the LED classdev API. The parent `rtl8366rb_setup()` calls `rtl8366rb_setup_leds()` unless LEDs are disabled globally by DT; with the Kconfig option disabled, the header supplies a no-op.

Risks: switching any LED in a group to manual force mode changes the trigger mode for the entire group across ports, which can disable hardware activity/speed indication unexpectedly. `kasprintf()` allocates `init_data.devicename` without an explicit free in this function. Errors from applying default state are not checked before registration. The debug/error messages sometimes print group and port values in a confusing order.

Test signals: DT LED nodes with `reg` 0 through 3 should create named LED class devices, invalid `reg` should warn and fail, default-state `on`/`off`/`keep` should match hardware bits, brightness writes should update the corresponding manual register bits, and using a manual LED should set its group mode to `RTL8366RB_LEDGROUP_FORCE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366rb-leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366rb.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366rb.c

Purpose: this is the RTL8366RB DSA subdriver for Realtek switches reachable through the shared SMI/MDIO infrastructure. It detects and resets RTL8366RB hardware, applies silicon/router-specific vendor jam tables, configures the CPU tag port, handles VLAN/member-table backends for `rtl8366-core`, controls bridge isolation, exposes MIB counters, supports optional LEDs, handles nested interrupts, and registers SMI and MDIO front-end drivers.

Important APIs, types, and functions: `rtl8366rb_setup()` is the main DSA setup path. `rtl8366rb_detect()` identifies RTL8366RB versus unsupported RTL8366S, sets CPU port/port count/VLAN table sizes/MIB counters, and resets the chip. MIB handling is in `rtl8366rb_get_mib_counter()`. IRQ support is implemented by `rtl8366rb_setup_cascaded_irq()`, `rtl8366rb_irq()`, and mask/unmask callbacks. VLAN hardware methods include `rtl8366rb_get_vlan_4k()`, `rtl8366rb_set_vlan_4k()`, `rtl8366rb_get_vlan_mc()`, `rtl8366rb_set_vlan_mc()`, `rtl8366rb_get_mc_index()`, `rtl8366rb_set_mc_index()`, `rtl8366rb_enable_vlan()`, and `rtl8366rb_enable_vlan4k()`. Phylink and DSA callbacks cover tag protocol, bridge join/leave, VLAN filtering, learning, STP, fast age, port enable/disable, and MTU.

Control flow: detection reads a legacy chip-ID register, rejects RTL8366S, initializes private Realtek limits for RTL8366RB, and hardware-resets via `RTL8366RB_RESET_CTRL_REG`. Setup confirms chip ID/version, chooses a version-specific jam table or a router-specific override for Belkin F5D8235 or Netgear DGN3500, writes the jam table with PHY-window handling for BE-prefixed registers, isolates all user ports to the CPU and lets the CPU reach all user ports, applies green Ethernet setup, writes undocumented vendor defaults, sets a random switch MAC address, enables the CPU tag port, initializes max frame size and per-port max MTU cache, disables learning, enables ageing, configures port 4 IO mode, opens VLAN ingress filters by default, configures LED blink/default LED behavior, resets VLAN state, attempts cascaded IRQ setup, and registers the internal user MDIO bus.

State and persistence: `struct rtl8366rb` stores per-port `max_mtu`, PVID-enabled flags, and optional LED classdev state. Hardware persistence covers CPU tag register state, port enable bits, port isolation matrices, learning disable bits, ageing/security bits, VLAN 4K and 16-entry member configuration tables, per-port MC indices, ingress VLAN filtering/drop controls, STP state per FID, MIB counters, LED mode/manual registers, interrupt mask/status/polarity registers, and PHY access state. The driver updates `pvid_enabled` to coordinate PVID and untagged-drop behavior when VLAN filtering is active.

Dependencies and integration points: the file depends on Realtek common transport and `rtl83xx` helpers, the shared `rtl8366-core` VLAN/stat callbacks, optional `rtl8366rb-leds`, DSA, phylink, bridge flags, irqdomain nested IRQs, OF interrupt children, and Realtek tag protocol `DSA_TAG_PROTO_RTL4_A`. Both SMI and MDIO front-end drivers use the same `rtl8366rb_variant`.

Risks: initialization depends on vendor jam tables and machine-compatible overrides, so unexplained register writes are hard to audit. The nested IRQ setup creates mappings only for `priv->num_ports` despite a 14-line domain, while status bits include non-port events. VLAN hardware has a 16-entry member table over a 4K VID table, creating allocation pressure and subtle PVID interactions. The FDB is not managed here; bridge isolation and learning bits carry most forwarding behavior. The random switch MAC is regenerated on setup, not persisted. Unsupported RTL8366S detection returns `-ENODEV`.

Test signals: expected logs should show RTL8366RB ID/version and successful jam-table setup. Validate CPU port traffic with RTL4_A tags, user-port isolation before bridge join, bridge join/leave forwarding masks, VLAN filtering with PVID versus no PVID, tagged/untagged VLAN add/delete through `rtl8366-core`, port enable/disable, STP and fast-age behavior, MTU threshold transitions across 1522/1536/1552/16000 settings, MIB counter reads under traffic, LED classdev behavior when enabled, and link-change interrupt propagation from the cascaded controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366rb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366rb.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366rb.h

Purpose: this header centralizes RTL8366RB constants and private structures shared by the main switch driver and optional LED companion. It defines port counts, LED register layouts, LED group trigger modes, conditional LED class state, and the main per-chip private data structure.

Important APIs, types, and functions: constants include `RTL8366RB_PORT_NUM_CPU`, `RTL8366RB_NUM_PORTS`, `RTL8366RB_PHY_NO_MAX`, `RTL8366RB_NUM_LEDGROUPS`, and LED control register/mask macros. `enum rtl8366_ledgroup_mode` lists all hardware LED trigger modes plus manual force mode. When LED support is enabled, `struct rtl8366rb_led` stores port/group, parent `realtek_priv`, and `led_classdev`, and `rtl8366rb_setup_leds()` is declared; otherwise a no-op inline is provided. `struct rtl8366rb` stores per-port max MTU, PVID state, and optional LED arrays. `rb8366rb_set_ledgroup_mode()` is declared for both LED-enabled and disabled builds.

Control flow: the header has no runtime flow, but it determines compile-time behavior. The main driver always can call `rtl8366rb_setup_leds()` safely because the no-op inline is selected without LED support. LED control code uses the register/mask macros to select one of two packed manual-control registers and to change shared group trigger mode.

State and persistence: `struct rtl8366rb` is allocated as `variant->chip_data_sz` behind `struct realtek_priv`. Its `max_mtu` cache mirrors the largest requested per-port MTU calculation, `pvid_enabled` mirrors whether each port has a nonzero member-config index, and optional `leds` stores LED classdev registrations and fixed port/group identity. Hardware LED state persists in registers defined here.

Dependencies and integration points: this header includes `realtek.h` for `struct realtek_priv` and is consumed by `rtl8366rb.c` and `rtl8366rb-leds.c`. It integrates with Kconfig symbol `CONFIG_NET_DSA_REALTEK_RTL8366RB_LEDS`, the LED subsystem, and Realtek regmap code.

Risks: LED group trigger mode is global per group, so the API can make all LEDs in a group manual even when a single LED is changed. The header exposes a function name `rb8366rb_set_ledgroup_mode()` with the apparent `rtl` prefix typo omitted, so callers must match that spelling. `pvid_enabled` is a software mirror and must stay synchronized with MC-index programming.

Test signals: build with and without `CONFIG_NET_DSA_REALTEK_RTL8366RB_LEDS`, verify `chip_data_sz` includes or excludes LED arrays as intended, check LED group register masks for all four groups, and validate max-MTU/PVID arrays cover all six ports including the CPU port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl8366rb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl83xx.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl83xx.c

Purpose: this is the common Realtek DSA support module for newer RTL83xx-style shared infrastructure. It provides regmap locking helpers, user-facing internal MDIO bus registration, common probe allocation and reset handling, DSA switch registration/unregistration, shutdown behavior, and reset-control/GPIO helpers used by Realtek SMI/MDIO front ends.

Important APIs, types, and functions: exported symbols include `rtl83xx_lock()`, `rtl83xx_unlock()`, `rtl83xx_setup_user_mdio()`, `rtl83xx_probe()`, `rtl83xx_register_switch()`, `rtl83xx_unregister_switch()`, `rtl83xx_shutdown()`, `rtl83xx_remove()`, `rtl83xx_reset_assert()`, and `rtl83xx_reset_deassert()`. Internal MDIO callbacks `rtl83xx_user_mdio_read()` and `rtl83xx_user_mdio_write()` delegate to `priv->ops->phy_read` and `priv->ops->phy_write`.

Control flow: common probe obtains the matched `realtek_variant`, allocates `struct realtek_priv` plus variant chip data, initializes a mutex-backed 16-bit big-endian regmap and a no-lock mirror regmap, stores variant ops and chip data pointers, reads `realtek,disable-leds`, obtains optional reset control and reset GPIO, stores driver data, and toggles reset if either reset mechanism exists. Registration calls the variant `detect()` method, fills DSA switch fields, and invokes `dsa_register_switch()`. Shutdown calls `dsa_switch_shutdown()` and clears drvdata so remove paths do not double-run.

State and persistence: the main persistent state is `struct realtek_priv`, including `map`, `map_nolock`, `map_lock`, variant ops, device pointer, chip-specific storage, optional reset handles, `leds_disabled`, DSA switch, and optional user MDIO bus. The no-lock regmap is intentionally used inside explicitly locked register sequences, especially indirect PHY access in chip drivers. Reset helper state is external hardware reset line state only.

Dependencies and integration points: the file depends on Linux regmap, OF MDIO, reset controls, GPIO descriptors, DSA, and `realtek_interface_info` transport callbacks supplied by SMI or MDIO bus wrappers. It exports namespace `REALTEK_DSA` for chip-specific modules.

Risks: the regmap config uses custom read/write callbacks and big-endian 10-bit register formatting; transport implementations must match that contract. Probe resets hardware before chip detection, so reset timing constants must be adequate across boards. The user MDIO bus requires an `mdio` child node and chip-specific PHY ops; missing nodes fail setup in callers. `rtl83xx_remove()` is currently empty, so all cleanup must be devm, DSA unregister, or chip-specific teardown.

Test signals: validate probe through both SMI and MDIO interface wrappers, check reset GPIO/control timing on boards with and without resets, verify locked versus no-lock regmap access with indirect PHY sequences, confirm internal MDIO bus registration under the switch `mdio` node, and ensure shutdown/remove do not double-unregister after bus-level shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl83xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl83xx.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl83xx.h

Purpose: this header declares the common RTL83xx Realtek DSA helper interface shared between transport front ends and chip-specific drivers.

Important APIs, types, and functions: `struct realtek_interface_info` carries transport-specific `reg_read` and `reg_write` callbacks used by `rtl83xx_probe()` to initialize regmap. The header declares lock/unlock helpers, user MDIO setup, common probe/register/unregister/shutdown/remove entry points, and reset assert/deassert helpers.

Control flow: there is no runtime implementation in the header. Its declarations define the sequence used by Realtek front-end drivers: probe allocates common state from `realtek_interface_info`, chip drivers register the DSA switch through `rtl83xx_register_switch()`, and teardown uses unregister/shutdown/remove helpers.

State and persistence: no state is stored in the header. The declared APIs operate on `struct realtek_priv`, DSA switch state, reset handles, and regmaps allocated in `rtl83xx.c`.

Dependencies and integration points: the header depends on declarations for `struct dsa_switch`, `struct realtek_priv`, and `struct device` from including translation units. It is included by RTL8365MB, RTL8366RB, LED support, and Realtek SMI/MDIO common code.

Risks: because the header provides only prototypes, build correctness depends on including it after headers that define the referenced types. Transport callbacks must follow the expected register/value contract used by the common regmap setup.

Test signals: compile coverage from all Realtek DSA modules, successful symbol resolution in namespace `REALTEK_DSA`, and runtime probe paths that pass valid transport callbacks into `rtl83xx_probe()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/rtl83xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/rzn1_a5psw.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/rzn1_a5psw.c

Purpose: this is the Renesas RZ/N1 Advanced 5-port Switch DSA driver. It manages the memory-mapped switch core, exposes four user ports plus fixed CPU port 4, uses the RZN1 A5PSW DSA tag, registers an optional internal MDIO bus, binds per-port MIIC PCS instances, manages bridge/FDB/VLAN offload, and exports MAC/RMON/control statistics.

Important APIs, types, and functions: `a5psw_probe()` allocates and registers the DSA switch. `a5psw_setup()` configures management forwarding, DSA tagging, lookup-table behavior, VLAN resources, and port defaults. Register helpers are `a5psw_reg_writel()`, `a5psw_reg_readl()`, and locked `a5psw_reg_rmw()`. DSA callbacks include port enable/disable, phylink caps/PCS/link up/down, ageing time, bridge join/leave/flags, STP state, FDB add/del/dump, VLAN filtering/add/del, stats callbacks, and MTU. MDIO is handled by `a5psw_probe_mdio()`, `a5psw_mdio_config()`, `a5psw_mdio_read()`, and `a5psw_mdio_write()`. PCS setup uses `miic_create()` from `pcs-rzn1-miic`.

Control flow: probe maps MMIO, initializes locks, sets the initial bridged mask to the CPU port, creates PCS objects for `pcs-handle` port properties, enables `hclk` and `clk`, optionally registers an MDIO bus from an `mdio` child node, fills `dsa_switch`, and registers it. Setup validates that CPU port index is 4, enables management port mode and management-forward pattern 0, enables A5PSW tagging for all frames, clears and enables lookup-table learning/ageing, resets learn count, clears all 32 VLAN resource entries, resets every port, enables only the CPU port initially, enables flooding/learning on the CPU port, places user ports in standalone isolated mode, and configures VLAN tag/input/output modes per active port.

State and persistence: `struct a5psw` stores MMIO base, clocks, device, optional MDIO bus, PCS pointers, DSA switch, lookup-table mutex, register RMW spinlock, bridged-port bitmap, and the single supported bridge device pointer. Hardware state includes management tag/config registers, lookup/FDB table and learn count, per-port authorization and enable bits, learning/blocking bits, flood masks, pattern matching, VLAN verify/in/out/resource/system-tag registers, command config, frame length, MDIO clock/command/data registers, and per-port statistics. FDB operations are serialized by `lk_lock`; generic register RMW sequences are serialized by `reg_lock`.

Dependencies and integration points: the file integrates with DSA, phylink, bridge flags/STP, switchdev VLAN/FDB callbacks, ethtool stats groups, `pcs-rzn1-miic`, OF port/PCS/MDIO nodes, common clocks, and `net/dsa/tag_rzn1_a5psw.c` through protocol `DSA_TAG_PROTO_RZN1_A5PSW`. It supports Device Tree compatible `renesas,rzn1-a5psw`.

Risks: hardware supports only one offloaded bridge; joining a second bridge returns `-EOPNOTSUPP`. FDB entries do not carry VID, so deleting the same MAC for one VID can remove forwarding for another VID; the code deliberately suppresses errors for invalid lookup on delete. VLAN resources are limited to 32 entries and deletion does not reclaim an entry when no ports remain. Stats use a shared high-word latch but do not take an explicit stats lock despite the header comment mentioning one. MDIO divider limits depend on `hclk` and requested `clock-frequency`. STP disables TX at the port-enable register while still allowing tagged BPDUs from the CPU path.

Test signals: verify DSA probe and fixed CPU port validation, RZN1 tag traffic through the management port, user-port standalone isolation before bridge join, single-bridge enforcement, bridge flag changes for learning and flood masks, STP transitions including BPDU behavior, static FDB add/delete/dump and fast-age flushing, VLAN add/filtering/PVID insertion across the 32-entry resource table, MDIO reads/writes and divider errors, PCS selection per user port, MAC/RMON/control stat growth, ageing time range validation, and clean PCS destruction on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/rzn1_a5psw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/rzn1_a5psw.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/rzn1_a5psw.h

Purpose: this header defines the Renesas RZ/N1 A5PSW register map, bitfields, limits, FDB entry packing, and private driver state used by `rzn1_a5psw.c`.

Important APIs, types, and functions: register macros cover global port enable, flood masks, VLAN verification and resource entries, management tag/control, lookup-table control/data/learn-count/ageing, MDIO config/command/data, per-port command/frame-length/status, and per-port statistics. `struct fdb_entry` and `union lk_data` map lookup-table data registers onto MAC/valid/static/priority/port-mask fields. `struct a5psw` stores MMIO base, clocks, device, MDIO bus, PCS array, DSA switch, locks, bridged-port mask, and bridge netdev pointer.

Control flow: the header itself has no runtime behavior, but its constants determine how the implementation sequences lookup-table reads/writes, VLAN resource manipulation, MDIO commands, port link command configuration, and stats reads. `A5PSW_PORT_OFFSET(port)` is the base macro for per-port register banks.

State and persistence: hardware state represented here includes the 8192-entry lookup table, 32 VLAN resources, five switch ports with CPU port 4, MDIO controller, 10 KiB jumbo frame limit, A5PSW 8-byte DSA tag allowance, and per-port counters. Software state in `struct a5psw` persists for the lifetime of the platform device and tracks bridge membership and allocated PCS/MDIO resources.

Dependencies and integration points: the header includes clock, platform, OF MDIO, `pcs-rzn1-miic`, and DSA headers because it declares `struct a5psw` with those types. It is tightly coupled to the A5PSW DSA driver and the RZN1 MIIC PCS provider.

Risks: several hardware limits are baked into macros: five ports, CPU port as the last port, 32 VLAN entries, 8192 FDB entries, and minimum MDIO divider 5. The packed FDB bitfield layout must match endianness and register layout assumptions. `A5PSW_EXTRA_MTU_LEN` reserves space for the DSA tag and two VLAN tags; incorrect accounting would cause unexpected drops or oversize acceptance.

Test signals: compile with the C driver, validate register offsets against the hardware manual, exercise FDB bitfield encoding by adding/dumping entries, test maximum MTU calculation, confirm CPU port index assumptions in DT, and check MDIO divider and VLAN resource limits at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/rzn1_a5psw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/Kconfig

Purpose: this Kconfig file declares build options for the NXP SJA1105/SJA1110 automotive Ethernet switch DSA driver and optional PTP, TAS, and Virtual Link features.

Important APIs, types, and functions: `CONFIG_NET_DSA_SJA1105` is a tristate depending on `NET_DSA`, `SPI`, and optional PTP clock infrastructure. It selects the SJA1105 DSA tagger, PCS XPCS, packing helpers, and CRC32. `CONFIG_NET_DSA_SJA1105_PTP` enables timestamping/PTP clock support. `CONFIG_NET_DSA_SJA1105_TAS` enables Time-Aware Scheduler offload and depends on PTP plus taprio. `CONFIG_NET_DSA_SJA1105_VL` enables Virtual Links and depends on TAS.

Control flow: build selection starts with the base SPI-managed DSA switch driver, then optional symbols layer feature-specific objects into the build through the Makefile. The TAS symbol enforces either built-in taprio support or modular DSA driver compatibility to avoid impossible linkage.

State and persistence: there is no runtime state in Kconfig. The selected symbols control which code is compiled into `sja1105.o`, which directly changes available driver behavior for PTP clocks, scheduled traffic, and flow classification.

Dependencies and integration points: this file integrates with kernel configuration symbols for DSA, SPI, PTP, taprio qdisc, tag protocols, PCS XPCS, packing, and CRC32. It documents supported switch revisions from SJA1105E/T/P/Q/R/S through SJA1110A/B/C/D.

Risks: optional feature dependencies matter because TAS relies on PTP and VL relies on TAS; misconfigured builds should be prevented by Kconfig. Enabling the base driver selects several helper subsystems, increasing build surface even for users not using all chip variants.

Test signals: run build matrix coverage for base-only, base+PTP, base+PTP+TAS, and full VL configurations; verify module/built-in combinations with `NET_SCH_TAPRIO`; and confirm selected tagger and helper libraries are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/Makefile

Purpose: this Makefile assembles the SJA1105/SJA1110 DSA driver object from common source files and conditionally includes feature modules for PTP, Time-Aware Scheduling, and Virtual Links.

Important APIs, types, and functions: `obj-$(CONFIG_NET_DSA_SJA1105) += sja1105.o` builds the composite object. Always-included objects are SPI transport, main driver, MDIO, flower classifier support, ethtool, devlink, clocking, static config, and dynamic config. Conditional additions are `sja1105_ptp.o`, `sja1105_tas.o`, and `sja1105_vl.o`.

Control flow: Kconfig symbol selection determines whether the composite object is omitted, built-in, or modular. Optional object inclusion follows feature symbols and therefore must match the prototypes and conditional declarations used by `sja1105.h` and related headers.

State and persistence: there is no runtime state. The build composition controls which runtime features and DSA callbacks are present in `sja1105.o`.

Dependencies and integration points: the Makefile is coupled to the SJA1105 Kconfig options and the C files in this directory. It ensures shared files such as `sja1105_clocking.c` and `sja1105_devlink.c` are present in every base-driver build.

Risks: because feature objects are linked into one composite driver, missing conditional guards in headers or source files can create unresolved symbols when optional features are disabled. The trailing backslash after `sja1105_dynamic_config.o` is accepted here because further conditional appends follow, but edits should preserve valid kbuild syntax.

Test signals: build `CONFIG_NET_DSA_SJA1105` as module and built-in, then repeat with each optional symbol enabled/disabled; inspect `sja1105.o` membership with verbose kbuild output when diagnosing missing symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105.h

Purpose: this is the central private header for the SJA1105/SJA1110 DSA driver. It defines shared constants, register address containers, chip capability descriptors, runtime private state, SPI transfer structures, reset reasons, clocking types, flow-rule models, and cross-file prototypes.

Important APIs, types, and functions: `struct sja1105_regs` maps per-chip register addresses for device ID, PTP, CGU/clocking, pads, stats, MDIO, and PCS. `struct sja1105_info` describes each chip variant: IDs, timestamp format, port count, tag protocol, dynamic/static table ops, register map, supported modes, internal PHY types, speeds, and function pointers for reset, FDB, PTP, clocking, PCS MDIO, and microcontroller disable. `struct sja1105_private` stores static config, RGMII delays, per-port PHY modes/fixed links, flood masks, timestamp flags, chip info, SPI device, DSA switch, PVIDs, flow-block state, locks, devlink regions, CBS entries, MDIO buses, PCS, PTP, and TAS data. The header also declares all major cross-file entry points for static/dynamic config, MDIO, devlink, SPI transfers, clocking, ethtool, FDB, and flower/VL handling.

Control flow: other SJA1105 source files include this header to share the selected `sja1105_info` and `sja1105_private` state. Main probe/setup code selects an `info` instance, builds `static_config`, registers MDIO/PCS/devlink, calls clocking and static-config upload paths, and uses reset reasons to reload static configuration after operations such as VLAN filtering, ageing-time changes, scheduling, policing, or virtual links.

State and persistence: the header defines the driver’s primary persistent state. `static_config` represents the switch configuration image uploaded to hardware. Per-port arrays persist PHY mode, fixed-link status, RGMII delay settings, bridge PVIDs, 8021q tag PVIDs, PCS pointers, and timestamp enable bits. Mutexes serialize management frames, FDB access, and dynamic config; a spinlock protects timestamp IDs. Devlink region pointers and optional PTP/TAS state persist until teardown.

Dependencies and integration points: dependencies include DSA, PTP/timecounter, DSA 802.1Q helpers, SJA1105 static/dynamic config headers, optional TAS/PTP headers, XPCS/MDIO through prototypes, SPI transfer code, devlink, ethtool, flower classifier, and Linux DSA tag definitions. Extern `sja1105_info` declarations connect this header to chip-specific data in other files.

Risks: this header is the coupling point for many optional features; conditional build coverage is important. Register address arrays must match chip families, with reserved addresses handled by implementation files. The static configuration model means some runtime changes require full config reloads, so state mirrors must remain synchronized before reload. RGMII delay conversion macros have a limited valid range and are tied to 1 Gbps clock assumptions.

Test signals: compile all optional feature combinations, probe each supported chip info path, validate static config reload reasons, verify dynamic config locking under concurrent bridge/FDB/flower operations, exercise PTP/TAS/VL when enabled, confirm per-port supported interface masks match DT, and inspect devlink/ethtool/MDIO/PCS integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_clocking.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_clocking.c

Purpose: this file programs the SJA1105/SJA1110 clock generation and pad configuration for MII, RMII, RGMII, and SGMII ports. It packs CGU register commands, selects clock sources/dividers based on MAC/PHY role and configured port speed, applies RGMII delay-line settings, configures pad electrical defaults, and provides an SJA1110 helper to disable the embedded microcontroller clocks.

Important APIs, types, and functions: key structures are `sja1105_cgu_idiv`, `sja1105_cgu_pll_ctrl`, `sja1105_cgu_mii_ctrl`, `sja1105_cfg_pad_mii`, `sja1105_cfg_pad_mii_id`, and `sja1110_cgu_outclk`. Packing helpers use `sja1105_packing()` for 4-byte command buffers. Public functions are `sja1105pqrs_setup_rgmii_delay()`, `sja1110_setup_rgmii_delay()`, `sja1105_clocking_setup_port()`, `sja1105_clocking_setup()`, and `sja1110_disable_microcontroller()`. Internal helpers program IDIV, MII TX/RX/ext clocks, RGMII TX clocks, RMII PLL/ref/ext clocks, and TX/RX pads.

Control flow: per-port setup reads XMII mode and MAC/PHY role from the static config `BLK_IDX_XMII_PARAMS`. MII mode configures IDIV depending on role, selects TX/RX clock sources, and for PHY role drives external TX/RX clocks from IDIV. RMII MAC role configures PLL1 for 50 MHz, disables IDIV, maps REF clock, and optionally maps external TX clock from PLL1; PHY role skips PLL1. RGMII setup reads static MAC speed: 1 Gbps disables IDIV and uses PLL0, 100 Mbps uses IDIV divide-by-1, 10 Mbps uses divide-by-10, auto speed skips CGU programming; then it configures RGMII TX clock, TX pads, and optional delay-line setup. SGMII requires no CGU action. Every port setup finishes by configuring RX pad pull behavior.

State and persistence: this file does not keep private software state, but it consumes `priv->static_config`, `priv->rgmii_rx_delay_ps`, `priv->rgmii_tx_delay_ps`, and `priv->info->regs`. Hardware state is in CGU IDIV/PLL/MII/RMII/RGMII clock registers and pad control/delay registers. SJA1105 P/Q/R/S delay setup uses a two-stage power-down/power-up sequence to recover delay lines across RGMII frequency changes; SJA1110 uses a different packing layout and inverted bypass semantics.

Dependencies and integration points: the file depends on `sja1105_xfer_buf()` SPI writes, `sja1105_packing()`, static config tables, chip-specific register maps, chip-specific speed encodings, and `sja1105_info` function pointers for RGMII delay setup and microcontroller disable. Main setup and phylink reconfiguration paths call these functions after static config speed/interface state is known.

Risks: clock programming is highly chip/register-map dependent; reserved addresses are skipped, so missing register definitions silently omit parts of setup. IDIV accepts only factors 1 or 10. RGMII delay conversion is constrained to the hardware delay range and assumes the delay values were validated earlier. RMII PLL1 sequencing must write setup with power-down then enable; failures leave RMII clocks absent. RGMII auto speed intentionally skips setup until speed is known, so link changes must trigger a later setup. SJA1110 delay packing differs from SJA1105 and must use the correct callback.

Test signals: validate MII MAC and PHY role clock source selections, RMII 50 MHz PLL/ref clock output, RGMII 10/100/1000 speed transitions, skipped setup for auto speed, RGMII internal delay values at min/max, pad register programming on all supported ports, SGMII no-op behavior, reserved-register chip variants, SPI write failures, and SJA1110 microcontroller clock gating of base timer and MCSS clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_clocking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_devlink.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_devlink.c

Purpose: this file adds devlink integration for SJA1105 by exposing the switch static configuration as a devlink region snapshot and reporting the ASIC identity through devlink info.

Important APIs, types, and functions: `sja1105_static_config_get_max_size()` constructs a dummy static config with every table set to maximum entry count and computes its packed length. `sja1105_region_static_config_snapshot()` allocates a buffer and serializes the current static config with `static_config_buf_prepare_for_upload()`. `sja1105_setup_devlink_regions()` creates devlink regions, `sja1105_teardown_devlink_regions()` destroys them, `sja1105_devlink_info_get()` reports `DEVLINK_INFO_VERSION_GENERIC_ASIC_ID`, and public setup/teardown wrappers are `sja1105_devlink_setup()` and `sja1105_devlink_teardown()`.

Control flow: setup allocates `priv->regions`, calculates each region size dynamically, and calls `dsa_devlink_region_create()` with one snapshot slot. The static-config snapshot path retrieves `priv` from the DSA devlink handle, computes the current packed length and maximum region length, allocates a maximum-sized zeroed buffer, and packs the current config into it. Teardown iterates registered regions and frees the region pointer array. Info-get simply writes the selected chip info name as the fixed ASIC ID.

State and persistence: persistent software state is `priv->regions`, an array of devlink region pointers. The exposed snapshot data is not live state; it is an allocated copy of `priv->static_config` serialized in hardware-upload format and freed by the region destructor. Region sizing is derived from table ops at setup/snapshot time to avoid hard-coded limits.

Dependencies and integration points: this file depends on DSA devlink helpers, SJA1105 static config table ops, static config serialization, and `priv->info->static_ops`/`device_id`. It is called by the main SJA1105 setup/teardown path and by devlink info callbacks in DSA.

Risks: if dummy static-config initialization fails, max size becomes zero and region creation or snapshot allocation may fail. The snapshot allocates `max_len` but packs only the current `len`, so consumers must interpret trailing zeroes based on serialized config format. Setup cleanup destroys already created regions but relies on `priv->regions` entries being initialized. Static config table max-entry metadata must stay in sync with serializer support.

Test signals: `devlink region show` should list `static-config`, snapshots should succeed and contain a parseable static-config image after setup and after config reloads, failed allocation paths should unwind created regions, and `devlink dev info` should report the selected SJA1105/SJA1110 chip name as the generic ASIC ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_devlink.c -->
