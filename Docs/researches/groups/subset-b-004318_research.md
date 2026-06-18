# Research: subset-b-004318

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2.c

Purpose: this is the Broadcom Starfighter 2 DSA switch platform driver. It binds BCM4908, BCM7445, and BCM7278 switch blocks to the DSA and b53 frameworks, maps the switch core/register/interrupt/FCB/ACB windows, registers a user MDIO bus, configures CPU and user ports, manages integrated GPHY power, and exposes phylink, bridge, VLAN, FDB, WoL, ethtool, and CFP hooks.

Important APIs, types, and functions: the runtime object is `struct bcm_sf2_priv` from `bcm_sf2.h`, backed by a `struct b53_device`. Key entry points are `bcm_sf2_sw_probe()`, `bcm_sf2_sw_remove()`, `bcm_sf2_sw_setup()`, `bcm_sf2_port_setup()`, `bcm_sf2_port_disable()`, `bcm_sf2_mdio_register()`, `bcm_sf2_sw_mac_config()`, `bcm_sf2_sw_mac_link_up()`, `bcm_sf2_sw_suspend()`, and `bcm_sf2_sw_resume()`. `bcm_sf2_ops` delegates many bridge/VLAN/FDB operations to b53 while adding SF2-specific port, interrupt, WoL, and RXNFC behavior.

Control flow: probe allocates private state, switch ops, b53 platform data, and b53 device glue; applies compatible-specific register offsets; maps six MMIO regions; enables optional clocks; resets the switch; discovers port modes from the `ports` node; registers an MDIO bus that can divert pseudo-PHY accesses; resets the CFP TCAM; disables and requests two interrupt banks; resets MIB counters; reads hardware revisions; and registers the b53 switch. DSA setup enables valid user ports, configures the IMP CPU port, disables unused ports, configures VLAN defaults, and enables ACB. Link changes program RGMII mode, flow control, speed/duplex override registers, and EEE initialization.

State and persistence: software state includes hardware parameters, per-port mode/link/enabled state, interrupt masks/status, MoCA and internal PHY masks, optional Broadcom tag mask, WoL port mask, MDIO bus pointers, clocks, reset control, and CFP state. Persistent hardware state includes core forwarding mode, port memory powerdown bits, RGMII controls, status override registers, ACB thresholds, interrupt masks, crossbar selection, MIB counters, and switch reset state. Suspend disables interrupts and ports and may gate the clock unless WoL is armed; resume resets hardware, reapplies crossbar/CFP/GPHY/setup state, and reenables clocks.

Dependencies and integration points: it integrates with platform/OF resources, common clock and reset APIs, DSA, b53, phylink, ethtool WoL/RXNFC, Broadcom PHY flags, mdio-unimac, IRQs, and the companion `bcm_sf2_cfp.c` classifier. Compatibles select per-SoC register layout and CFP rule count.

Risks: register offsets and core alignment differ by SoC and are critical for every MMIO access. The MDIO registration mutates OF phandle properties and unregisters pseudo-PHY devices for old BCM7445 behavior. Port 5 on BCM7278 is forcefully prevented from becoming a CPU port by removing an `ethernet` property. WoL changes port disable semantics and CPU port enablement. Resume relies on replaying DSA setup after a reset, so any missing shadow state can cause configuration loss.

Test signals: probe on all compatibles, correct register mapping and revision logging, MDIO user bus access including pseudo-PHY diversion, user/CPU port enable and disable, phylink speed/duplex/pause transitions, MoCA IRQ link notifications, bridge/VLAN/FDB delegation through b53, WoL suspend/resume behavior, CFP rule restoration after resume, clock rate recalculation as ports become active, and clean remove/shutdown with reset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2.h

Purpose: this header defines the private Broadcom Starfighter 2 switch contract shared by the main SF2 driver and the CFP classifier. It describes hardware parameters, per-port status, classifier state, register access helpers, interrupt mask helpers, and CFP entry points exported to DSA ethtool hooks.

Important APIs, types, and functions: `struct bcm_sf2_hw_params` stores detected top/core/GPHY revisions and port/resource counts. `struct bcm_sf2_port_status` caches PHY interface, link, and enabled state. `struct bcm_sf2_cfp_priv` owns the classifier lock, used and unique rule bitmaps, rule count, and rule list. `struct bcm_sf2_priv` is the central driver state, including MMIO bases, reset/clock handles, b53 device, IRQ masks, MDIO buses, masks for internal PHYs, Broadcom tags and WoL, and CFP state. Inline helpers include `bcm_sf2_to_priv()`, `bcm_sf2_mangle_addr()`, `core_readl()/core_writel()`, `reg_readl()/reg_writel()`, generated `*_readl()` helpers, 64-bit latched accessors, and `intrl2_*_mask_set/clear()`.

Control flow: C files include this header to translate DSA switch pointers to SF2 state, read and write the switch core and ancillary register windows, protect latched 64-bit accesses with `indir_lock`, and maintain software interrupt-mask shadows while programming INTRL2 mask registers. The prototypes at the bottom connect `bcm_sf2.c` ethtool callbacks to `bcm_sf2_cfp.c`.

State and persistence: the header itself stores no state, but it defines the fields that persist across runtime operations and resume replay. Important shadow state includes register offset tables, core register alignment, IRQ masks, port status, MDIO routing masks, WoL mask, and CFP rule bitmaps/list.

Dependencies and integration points: it depends on platform devices, I/O accessors, locks, MII, ethtool, VLAN definitions, reset controls, DSA, `bcm_sf2_regs.h`, and b53 private definitions. It is the local ABI between the SF2 bus glue, b53 switch core, and CFP support.

Risks: the generated 64-bit accessors rely on REG_DIR_DATA_READ/WRITE latching and only provide relative atomicity through `indir_lock`. Interrupt mask helpers update software shadows and hardware masks in a specific order. `reg_readl()` uses compatible-provided offset tables; missing offsets silently become offset zero if the table is incomplete.

Test signals: compile coverage of both SF2 C files, 32/64-bit MIB access correctness, interrupt mask shadow consistency, CFP lock/list initialization, and valid register offset tables for every compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2_cfp.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2_cfp.c

Purpose: this file implements Broadcom SF2 Content Flow Processor support for ethtool RX flow classification. It programs TCAM, action/policer RAM, UDF layouts, per-rule counters, and software rule bookkeeping for TCP/UDP IPv4 and IPv6 filters, including VLAN-qualified matches and queue/port steering.

Important APIs, types, and functions: `struct cfp_rule` stores the source port and ethtool flow spec in the software list. UDF layouts describe how packet bytes map into CFP slices for IPv4 and IPv6. Main helpers include `bcm_sf2_cfp_op()`, `bcm_sf2_cfp_rule_addr_set()`, `bcm_sf2_cfp_act_pol_set()`, `bcm_sf2_cfp_ipv4_rule_set()`, `bcm_sf2_cfp_ipv6_rule_set()`, `bcm_sf2_cfp_rule_set()`, `bcm_sf2_cfp_rule_del()`, `bcm_sf2_get_rxnfc()`, `bcm_sf2_set_rxnfc()`, `bcm_sf2_cfp_rst()`, `bcm_sf2_cfp_resume()`, and CFP ethtool statistic functions.

Control flow: set operations lock `priv->cfp.lock`, validate unsupported extensions, reject occupied locations, compare against existing rules, allocate a rule, then insert hardware entries. IPv4 rules use one TCAM entry. IPv6 rules reserve two rule indexes, program a source-address slice first, then program a destination-address slice chained by `CHAIN_ID`, returning only the unique second-half location to userspace. Action RAM can replace the ARL destination with a specified port/queue and loop back when source and destination ports match. Delete operations clear the TCAM valid bits, remove chained companions, update bitmaps, and free the software rule. Resume clears hardware CFP enablement, resets TCAM, removes stale hardware entries, and reinserts every software rule.

State and persistence: software persistence is the rule list and `used`/`unique` bitmaps, with rule zero permanently reserved. Hardware persistence includes per-port UDF programming, TCAM data/mask ports, action and policer RAMs, rate meter disable state, CFP enable map, and green/yellow/red statistic RAM. VLAN-qualified rules may also install egress VLAN state through DSA VLAN callbacks.

Dependencies and integration points: it uses ethtool RXNFC APIs, flow dissector conversion, switchdev VLAN objects, DSA conduit ethtool passthrough, b53/SF2 register helpers, and CFP constants from `bcm_sf2_regs.h`. Successful local classifier changes are passed to the conduit netdev when supported, with rollback on conduit failure.

Risks: IPv6 consumes two hardware entries but exposes one location, so unique/used bitmap handling is critical. Error paths after the first IPv6 entry must clear reserved bits and destroy generated flow rules. VLAN rule insertion can modify switch VLAN state without an explicit rollback path for later CFP programming failures. Mask inversion is needed when returning ethtool rules because hardware and ethtool use opposite mask conventions. CFP operations busy-wait with finite timeouts, and per-port UDF layouts are shared hardware state.

Test signals: add/get/delete/list TCPv4, UDPv4, TCPv6, and UDPv6 rules; explicit and automatic locations; duplicate detection; VLAN-qualified filter steering and egress tag flag handling; invalid discard/unsupported flow handling; conduit ethtool rollback; CFP counter reads; TCAM reset timeout behavior; and suspend/resume rule restoration including IPv6 chained entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2_cfp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2_regs.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2_regs.h

Purpose: this header defines the Broadcom Starfighter 2 register IDs, offsets, bit fields, and resource constants used by the SF2 platform driver and CFP classifier. It covers the register indirection table, switch control/status, GPHY control, crossbar selection, LEDs, RGMII controls, interrupt banks, ACB queues, core forwarding and port state, VLAN/FDB/MIB-related core registers, CFP TCAM/action/rate/stat RAM, UDF layout registers, and global resource sizes.

Important APIs, types, and functions: `enum bcm_sf2_reg_offs` names logical offsets in the `reg_offsets` tables. Macros such as `MDIO_MASTER_SEL`, `PHY_RESET`, `RGMII_MODE_EN`, `P_IRQ_MASK()`, `ACB_QUEUE_CFG()`, `CORE_G_PCTL_PORT()`, `CORE_STS_OVERRIDE_GMIIP_PORT()`, `CORE_PORT_TC2_QOS_MAP_PORT()`, `CORE_CFP_DATA_PORT()`, `CORE_CFP_MASK_PORT()`, and CFP action/rate/stat bits are consumed directly by the C files. Constants define `UDF_NUM_SLICES`, `UDFS_PER_SLICE`, `CFP_NUM_RULES`, and `SF2_NUM_EGRESS_QUEUES`.

Control flow: the main driver uses these definitions to reset the switch, power ports and GPHYs, program IMP forwarding, configure traffic class to queue mapping, set link overrides, configure ACB thresholds, process interrupts, and expose b53 core access. The CFP driver uses the TCAM access register, data/mask ports, UDF offsets, action policy fields, policer disable mode, and statistic RAM selectors to create hardware flow rules.

State and persistence: the header documents persistent hardware state rather than storing it. Relevant state includes switch control and revision registers, port memory power state, link/speed/duplex overrides, LED control policy, interrupt mask/status, ACB thresholds, VLAN table entries, CFP table contents, UDF configuration, and per-rule counters.

Dependencies and integration points: it is included by `bcm_sf2.h`, `bcm_sf2.c`, and `bcm_sf2_cfp.c`. The logical `REG_*` enum is tied to the compatible-specific offset arrays in `bcm_sf2.c`.

Risks: bitfield definitions are hardware ABI. Typographical or shift/mask mistakes directly corrupt MMIO programming. Some macros encode SoC-specific alternate layouts, such as `CORE_STS_OVERRIDE_IMP2` and BCM4908 crossbar fields. The register enum must remain synchronized with all offset arrays.

Test signals: compile-time use across SF2 files, probe and register dump sanity on each compatible, interrupt status/mask correctness, ACB threshold programming, link override behavior, CFP TCAM programming and counters, and LED/GPHY/RGMII control writes matching hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/bcm_sf2_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/dsa_loop.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/dsa_loop.c

Purpose: this is a DSA loopback/mock switch driver. It creates a synthetic switch on the fixed MDIO bus, registers fixed PHYs, exposes basic DSA operations, tracks VLAN and PHY-access state, and is mainly useful for DSA framework development and lockdep coverage rather than real packet switching.

Important APIs, types, and functions: `struct dsa_loop_priv` stores the MDIO bus, VLAN table, conduit netdev, and per-port MIB/PVID/MTU state. `struct dsa_loop_vlan` tracks members and untagged ports. Entry points include `dsa_loop_init()`, `dsa_loop_create_switch_mdiodev()`, `dsa_loop_drv_probe()`, `dsa_loop_setup()`, `dsa_loop_phy_read()`, `dsa_loop_phy_write()`, VLAN add/delete/filtering callbacks, MTU callbacks, devlink VTU resource helpers, and module exit cleanup.

Control flow: module init creates an MDIO device at address 31 on bus `fixed-0`, stores platform data naming four LAN ports and an `eth0` CPU conduit, registers fixed PHYs, then registers an MDIO driver whose bus match only accepts this driver. Probe obtains the conduit netdev, fills the CPU port netdev pointer, allocates a DSA switch, attaches loop ops, and registers it. DSA setup initializes per-port MIB names and registers a devlink VTU resource. VLAN add/delete mutate the software VLAN table and deliberately perform a sleeping MDIO read to exercise locking constraints.

State and persistence: all state is volatile module state: global fixed PHY pointers, global switch MDIO device, per-port MIB counters, per-port PVID/MTU, and the software VLAN table. Devlink occupancy reports non-empty VLAN entries. Remove unregisters DSA and drops the conduit netdev reference; module exit unregisters the MDIO driver, fixed PHYs, and MDIO device.

Dependencies and integration points: it uses DSA, fixed PHY, MDIO, phylink, bridge/VLAN switchdev objects, devlink resources, and an existing `eth0` netdev. It returns `DSA_TAG_PROTO_NONE` and supports broad phylink capabilities for test flexibility.

Risks: the hardcoded `fixed-0` bus, MDIO address 31, and `eth0` conduit make it environment-specific. There is no real hardware forwarding, so state only exercises DSA callbacks. VLAN delete does not range-check `vlan->vid` while add does. The init path must unwind fixed PHYs and MDIO device registration correctly on failure.

Test signals: module load/unload, fixed PHY registration, DSA switch registration, devlink VTU occupancy changes after VLAN operations, ethtool stats for PHY read/write success and errors, bridge and STP callback logging, MTU set/get behavior, and lockdep validation around sleeping VLAN callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/dsa_loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/Kconfig

Purpose: this Kconfig entry exposes the Hirschmann Hellcreek TSN switch driver as `NET_DSA_HIRSCHMANN_HELLCREEK`. It controls whether the Hellcreek DSA platform driver, PTP support, hardware timestamping, LED integration, TAPRIO offload support, and Hellcreek tagging support can be built.

Important APIs, types, and functions: the single config symbol is a tristate named "Hirschmann Hellcreek TSN Switch support". It depends on `HAS_IOMEM`, `NET_DSA`, `PTP_1588_CLOCK`, `LEDS_CLASS`, and `NET_SCH_TAPRIO`, and selects `NET_DSA_TAG_HELLCREEK`.

Control flow: when enabled, the Makefile builds `hellcreek_sw.o` from `hellcreek.o`, `hellcreek_ptp.o`, and `hellcreek_hwtstamp.o`. Selecting the tagger ensures DSA can parse and emit the Hellcreek-specific CPU-port tag format required by the driver.

State and persistence: this file stores no runtime state. It determines whether the driver is compiled in, built as a module, or omitted, and whether required framework symbols must be enabled.

Dependencies and integration points: the dependencies mirror runtime driver needs: MMIO register access, DSA switch registration, PTP clock registration, LED class devices, and TAPRIO schedule offload. The selected tagger is the DSA integration point for packet metadata.

Risks: making PTP, LED, or TAPRIO hard dependencies means the switch driver is unavailable in smaller DSA builds lacking any one subsystem. Missing `NET_DSA_TAG_HELLCREEK` selection would make the driver unusable at runtime.

Test signals: Kconfig dependency resolution for built-in and module builds, automatic tagger selection, and successful compilation of the three-object Hellcreek switch module when all dependencies are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/Makefile

Purpose: this Makefile wires the Hellcreek driver objects into the kernel build when `CONFIG_NET_DSA_HIRSCHMANN_HELLCREEK` is enabled.

Important APIs, types, and functions: `obj-$(CONFIG_NET_DSA_HIRSCHMANN_HELLCREEK) += hellcreek_sw.o` declares the composite module or built-in object. `hellcreek_sw-objs` includes `hellcreek.o`, `hellcreek_ptp.o`, and `hellcreek_hwtstamp.o`.

Control flow: Kbuild links the main DSA/platform driver, the PTP clock implementation, and hardware timestamp support into one driver unit named `hellcreek_sw`.

State and persistence: there is no runtime state. The file controls object composition and therefore which symbols are available inside the driver.

Dependencies and integration points: it is paired with `Kconfig` and relies on the three C files having internal symbol references such as `hellcreek_ptp_setup()`, `hellcreek_hwtstamp_setup()`, and DSA timestamp callbacks.

Risks: omitting any component breaks either link-time references or runtime functionality. The composite object name differs from the platform driver's `.driver.name` (`hellcreek`), so packaging or module-load expectations should follow Kbuild output rather than the platform driver name.

Test signals: `make drivers/net/dsa/hirschmann/` with the config enabled, module symbol resolution across the three objects, and `modinfo`/module load verifying the combined object registers the Hellcreek platform driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek.c

Purpose: this is the main Hirschmann Hellcreek TSN DSA switch driver. It manages MMIO switch-core access, DSA registration, port enablement, VLAN isolation, FDB programming, devlink resources and snapshots, phylink capabilities, bridge flags, STP, HSR hooks, and TAPRIO/Qbv schedule offload.

Important APIs, types, and functions: the driver uses `struct hellcreek`, `struct hellcreek_port`, and `struct hellcreek_fdb_entry` from `hellcreek.h`. Major functions are `hellcreek_probe()`, `hellcreek_setup()`, `hellcreek_port_enable()`, `hellcreek_vlan_add()/del()`, `hellcreek_vlan_filtering()`, `hellcreek_fdb_add()/del()/dump()`, `hellcreek_setup_devlink_resources()`, `hellcreek_setup_devlink_regions()`, `hellcreek_port_set_schedule()`, `hellcreek_port_del_schedule()`, and `hellcreek_port_setup_tc()`. `hellcreek_ds_ops` binds the DSA method table, including PTP/hwtstamp callbacks from companion files.

Control flow: probe allocates switch and per-port state, maps `tsn` and `ptp` resources, detects the module ID, waits for readiness, derives FDB size, initializes the DSA switch, registers it, then sets up PTP and timestamping. DSA setup enables the IP core, enables CPU/tunnel ports, configures learning/aging/DSA tagging/length-aware shaping, installs private VLAN memberships for standalone port separation, maps PCP to identical traffic classes, installs static PTP/STP multicast FDB entries, and registers devlink resources and regions. TAPRIO replace stores a schedule copy, programs max SDU, gate control list, cycle time, and either arms the schedule immediately or starts delayed polling until the base time is close enough.

State and persistence: persistent software state includes `swcfg`, per-port `ptcfg` shadows, `vidmbrcfg` VLAN membership shadow for all VIDs, per-port VLAN-device bitmaps, cumulative counter values, current TAPRIO schedules, delayed schedule work, and devlink region handles. Hardware state includes selected port/VLAN/counter/TGD registers, port config, switch config, FDB table, VLAN membership table, counter read latches, and Qbv gate/cycle/base-time registers.

Dependencies and integration points: it depends on platform OF match data, DSA, phylink, bridge/VLAN switchdev, devlink resources/regions, ethtool stats, HSR simple helpers, TAPRIO offload, and companion Hellcreek PTP/hwtstamp modules. The only in-tree compatible here is `hirschmann,hellcreek-de1soc-r1`.

Risks: several hardware reads advance internal pointers, so FDB operations must stay serialized under `reg_lock`. Private VLANs reserve high VIDs and the pre-changeupper path denies duplicate VLAN subinterfaces across ports to preserve separation. VLAN awareness is global, limiting mixed filtering modes. Schedule arming relies on the software PTP seconds/nanoseconds cache and delayed work for far-future base times. Resource teardown must destroy devlink regions before unregistering resources.

Test signals: platform probe with correct module ID, DSA setup and port isolation, bridge join/leave, VLAN add/delete including restricted VID rejection, FDB add/delete/dump with multi-port masks, PTP multicast interception, devlink resource occupancy and region snapshots, ethtool counter accumulation, STP and flood flag behavior, phylink capability reporting for 100M and 1G variants, TAPRIO replace/destroy including delayed arming, and clean remove/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek.h

Purpose: this header defines the Hellcreek switch register map, port constants, TSN/Qbv register bits, devlink structures, and private state shared by the main driver, PTP clock code, and hardware timestamping code.

Important APIs, types, and functions: constants define CPU and tunnel ports, VLAN membership encodings, egress queue count, default max SDU, switch-core registers (`HR_*`) and TSN gate registers (`TR_*`). Core types include `struct hellcreek_counter`, `struct hellcreek_port_hwtstamp`, `struct hellcreek_port`, `struct hellcreek_fdb_entry`, `struct hellcreek`, and `struct hellcreek_devlink_vlan_entry`. Macros such as `dw_to_hellcreek_port()` support delayed schedule work ownership.

Control flow: C files use the register definitions to select ports, VLANs, counters, FDB entries, and time-gate domains, and use the shared structs to coordinate DSA operations, PTP overflow work, LED state, per-port timestamp queues, and TAPRIO delayed work.

State and persistence: the header defines the complete driver state layout: platform data, DSA switch, PTP clock and clock info, per-port array, overflow work, LEDs, three mutexes, devlink regions, TSN and PTP MMIO bases, software shadows for switch config, VLAN membership, PTP seconds/last timestamp, status outputs, and FDB size. Per-port state includes VLAN-device bitmap, port config shadow, counters, hwtstamp state, current schedule, and delayed work.

Dependencies and integration points: it includes bitmap/bitops/device/LED/mutex/PTP/timecounter/workqueue types, Hellcreek platform data, DSA, and packet scheduler TAPRIO definitions. It is the common local ABI for `hellcreek.c`, `hellcreek_ptp.c`, and `hellcreek_hwtstamp.c`.

Risks: register bit definitions are hardware ABI and many fields are selected indirectly through current port/priority/VLAN/TGD selectors, so callers must serialize and program selectors correctly. The PTP and TSN schedule code share time state through `ptp_lock`. A typo in `TR_EETCMD_EETSEC_MASK` uses `GEMASK`, which would be compile-sensitive if that macro path is used.

Test signals: build coverage of all Hellcreek files, correct struct sharing across object boundaries, register programming validation for FDB/VLAN/Qbv/PTP, lockdep coverage for `reg_lock`, `vlan_lock`, and `ptp_lock`, and devlink snapshot structure size compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_hwtstamp.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_hwtstamp.c

Purpose: this file implements Hellcreek hardware timestamp integration for DSA. It advertises timestamp capabilities, validates per-port hwtstamp configuration, queues TX and RX PTP packets, reads hardware timestamp registers, reconstructs full nanosecond time using the PTP software seconds tracker, and delivers timestamps through normal skb timestamp APIs.

Important APIs, types, and functions: exported DSA callbacks are `hellcreek_get_ts_info()`, `hellcreek_port_hwtstamp_set()`, `hellcreek_port_hwtstamp_get()`, `hellcreek_port_txtstamp()`, `hellcreek_port_rxtstamp()`, `hellcreek_hwtstamp_work()`, `hellcreek_hwtstamp_setup()`, and `hellcreek_hwtstamp_free()`. Internal helpers include `hellcreek_should_tstamp()`, `hellcreek_ptp_hwtstamp_available()`, `hellcreek_ptp_hwtstamp_read()`, `hellcreek_txtstamp_work()`, and `hellcreek_get_rxts()`.

Control flow: users configure timestamping through DSA hwtstamp callbacks; unsupported modes are rejected or normalized to the hardware-supported PTPv2 event filter and TX-on mode. TX timestamping clones eligible PTP skbs, allows only one outstanding TX timestamp per port, stores start jiffies, and schedules the PTP worker. The worker polls port-specific TX status/data registers until available or timeout, then completes the clone with a hardware timestamp. RX timestamping accepts eligible PTP packets, stores the PTP class in skb control data, queues the skb, and the worker reads the inline reserved-field nanoseconds, clears the field, adds the seconds component, and injects the skb with `netif_rx()`.

State and persistence: per-port `hellcreek_port_hwtstamp` stores state bits, RX queue, TX start time, TX skb clone, and current config. Hardware state includes timestamp source settings, inline reserved-field timestamping, TX status/data registers, and RX inline timestamp insertion. Full timestamps depend on PTP `seconds` and `last_ts` maintained by `hellcreek_ptp.c`.

Dependencies and integration points: it depends on DSA timestamp callbacks, `ptp_classify_raw()`, `ptp_parse_header()`, PTP worker scheduling, skb hwtstamp helpers, Hellcreek PTP register access, and state from `hellcreek.h`.

Risks: only ports 2 and 3 are handled for TX timestamp register selection. One outstanding TX timestamp per port is allowed; extra timestampable packets are dropped from timestamp service. RX uses `skb->cb` to store PTP type and uses the PTP reserved field as a temporary timestamp carrier. Timestamp reconstruction around nanosecond rollover depends on the software seconds tracker being fresh. TX timeout frees the clone after 40 ms.

Test signals: `ethtool -T` capability reporting, accepted and rejected hwtstamp configs, TX PTP event timestamp delivery and timeout behavior, RX PTPv2 L2/L4 event timestamping with reserved field clearing, concurrent timestamp attempts per port, timestamp rollover near one-second boundaries, and setup programming of `PR_SETTINGS_C`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_hwtstamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_hwtstamp.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_hwtstamp.h

Purpose: this header defines Hellcreek timestamp register offsets, timestamp status bits, skb metadata access, TX timeout policy, and exported hardware timestamping functions used by the main Hellcreek DSA driver and PTP worker.

Important APIs, types, and functions: register constants cover RX/TX status and data registers for front ports 1 and 2. `PR_TS_STATUS_TS_AVAIL` and `PR_TS_STATUS_TS_LOST` decode timestamp status. `SKB_PTP_TYPE()` stores an unsigned PTP class in `skb->cb`. `TX_TSTAMP_TIMEOUT` limits TX polling to 40 ms. Prototypes expose hwtstamp set/get, TX/RX timestamp callbacks, ethtool timestamp info, PTP worker callback, setup, and free.

Control flow: `hellcreek.c` installs the prototypes in `hellcreek_ds_ops`, while `hellcreek_ptp.c` assigns `hellcreek_hwtstamp_work()` as `ptp_clock_info.do_aux_work`. `hellcreek_hwtstamp.c` uses the register constants and timeout during worker-driven timestamp completion.

State and persistence: this file stores no state. It defines how per-port hwtstamp state in `struct hellcreek_port_hwtstamp` interacts with hardware timestamp status/data registers and skb control metadata.

Dependencies and integration points: it includes DSA and `hellcreek.h`, and relies on PTP clock types through function signatures. It is the interface boundary between DSA hwtstamp operations and the Hellcreek PTP worker.

Risks: `skb->cb` ownership must not conflict with other consumers before the packet is reinjected. The register map only names two user ports, matching current platform data. Timeout selection affects whether delayed TX timestamps are delivered or discarded.

Test signals: compile/link coverage across Hellcreek objects, TX status available/lost handling, timeout behavior, RX skb control field preservation until worker execution, and correct register selection for ports 2 and 3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_hwtstamp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_ptp.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_ptp.c

Purpose: this file implements the Hellcreek PTP hardware clock and LED status outputs. It registers a PHC, reads and sets time, applies frequency and offset adjustments, tracks seconds in software around a hardware nanoseconds counter, schedules overflow maintenance, and registers two LED class devices backed by PTP status output bits.

Important APIs, types, and functions: exported helpers are `hellcreek_ptp_read()`, `hellcreek_ptp_write()`, `hellcreek_ptp_gettime_seconds()`, `hellcreek_ptp_setup()`, and `hellcreek_ptp_free()`. PTP operations include `hellcreek_ptp_gettimex()`, `hellcreek_ptp_settime()`, `hellcreek_ptp_adjfine()`, `hellcreek_ptp_adjtime()`, and `hellcreek_ptp_enable()`. Worker and LED helpers include `hellcreek_ptp_overflow_check()`, `hellcreek_led_setup()`, and brightness set/get callbacks.

Control flow: setup initializes delayed overflow work, fills `ptp_clock_info`, registers the PHC, enables hardware offset and drift correction, registers LEDs from the `leds` child node, and schedules periodic overflow checks. Time reads snapshot hardware, read several sync-data words, wrap system timestamp pre/post hooks around the low-nanoseconds read, update software seconds when nanoseconds roll over, and return full nanoseconds. Large time adjustments are converted to settime; smaller adjustments program slow offset correction registers. Frequency adjustments compute a drift addend from scaled ppm and program the drift register.

State and persistence: `hellcreek->seconds` and `hellcreek->last_ts` persist the high-order time component missing from hardware. `status_out` shadows LED output bits. The PTP clock registration persists until remove. Hardware persistence includes clock write, drift, offset, status, snapshot, and status output registers.

Dependencies and integration points: it integrates with Linux PTP clock core, system timestamp capture, delayed work, LED class devices and OF LED defaults, Hellcreek hwtstamp worker, and the `ptp_lock` shared with timestamping and TAPRIO schedule calculations.

Risks: hardware exposes only nanoseconds plus partial seconds, making periodic overflow checks essential. `hellcreek_ptp_gettime_seconds()` must infer whether a packet timestamp belongs to the current or previous software second. LED setup requires two available LED child nodes; failure unregisters the PHC. Adjfine arithmetic assumes a 125 MHz oscillator and hardware accumulator behavior.

Test signals: PHC registration and `phc2sys` reads, `settime`, small and large `adjtime`, positive and negative `adjfine`, rollover handling across seconds, hwtstamp timestamp reconstruction near rollover, PTP worker invocation, LED default-state parsing and brightness writes, and remove cleanup cancelling overflow work and unregistering LEDs/PHC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_ptp.h -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_ptp.h

Purpose: this header defines the Hellcreek PTP register map, adjustment constants, overflow interval, exported PTP helpers, and container macros used by PTP, hwtstamp, and main switch code.

Important APIs, types, and functions: constants define the 7 ns maximum step, slow-offset resource limit, quarter-second overflow period, PTP settings/command/status/read/write/offset/drift/snapshot registers, and `STATUS_OUT` LED bits. Prototypes expose setup/free, raw PTP register read/write, and seconds reconstruction. Macros convert `ptp_clock_info`, delayed overflow work, and LED class devices back to `struct hellcreek`.

Control flow: `hellcreek_ptp.c` uses the constants to program the PHC and LEDs, while `hellcreek_hwtstamp.c` uses raw register helpers and `hellcreek_ptp_gettime_seconds()` for packet timestamps. `hellcreek.c` indirectly depends on the software time state for TAPRIO schedule start calculations.

State and persistence: the header stores no state, but defines persistent hardware clock and LED output registers and the policy that overflow maintenance runs four times per second.

Dependencies and integration points: it includes bit operations, PTP clock kernel types, and `hellcreek.h`. It is the local interface between the PHC implementation and the timestamping code.

Risks: constants encode assumptions about hardware step size, oscillator behavior, and available slow-offset resources. If overflow work is delayed beyond the hardware nanoseconds rollover window, seconds tracking can drift. Container macros require embedded struct names to remain stable.

Test signals: build/link across PTP and hwtstamp objects, register access at expected offsets, PHC adjustment limits, overflow worker cadence, LED status bit control, and timestamp seconds reconstruction through the exported helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ks8995.c -->
## sources/distributed-fs/ceph-client/drivers/net/dsa/ks8995.c

Purpose: this is an SPI DSA driver for Micrel/Kendin KS8995MA, KSZ8864RMN, and KSZ8795CLX Ethernet switches. It detects supported chip variants, controls optional reset GPIO, performs serialized SPI register access, registers a five-port DSA switch, exposes basic phylink, STP, learning, and MTU controls, and handles remove reset.

Important APIs, types, and functions: `struct ks8995_chip_params` captures family/chip IDs, register size, address width, and address shift for each variant. `struct ks8995_switch` stores the SPI device, DSA switch, mutex, reset GPIO, chip params, revision, and per-port MTU cache. Important functions are `create_spi_cmd()`, `ks8995_read()/write()`, `ks8995_read_reg()/write_reg()`, `ks8995_get_revision()`, `ks8995_reset()`, `ks8995_check_config()`, phylink MAC callbacks, bridge flag/STP callbacks, `ks8995_change_mtu()`, `ks8995_probe()`, and `ks8995_remove()`.

Control flow: probe selects the variant from the SPI ID table, allocates state, gets and deasserts reset GPIO, configures SPI mode and word size, verifies family and chip ID, resets the switch through ID1 start/stop writes, enables port 5 PHY mode, allocates and registers the DSA switch, and installs phylink ops. CPU-port link-up programs global control 4 for 10/100 and duplex. Bridge learning toggles the per-port learning-disable bit. STP state updates TX/RX enable and learning bits in port control 2. MTU changes compute the largest requested MTU across all ports and toggle global legal/huge packet bits.

State and persistence: software state is the chip descriptor, revision, mutex, reset GPIO, DSA pointer, and per-port requested MTUs. Hardware state persists in global control registers for switch start, port 5 PHY mode, CPU MII speed/duplex, huge/legal packet acceptance, and per-port control registers for TX/RX/learning. Remove unregisters DSA and asserts reset when available.

Dependencies and integration points: it uses SPI core, GPIO descriptors, OF/SPI ID matching, DSA, phylink, bridge flags, VLAN MTU constants, and netdev PHY interface definitions. It supports internal PHY interfaces on user ports and MII on the CPU port.

Risks: the OF match table lacks `.data`, so variant selection depends on the SPI device ID path. Register helpers collapse failed byte transfers to boolean-style errors, losing detailed SPI error codes. `ks8995_check_config()` returns success even if writing GC0 fails after logging. Tag protocol currently returns `DSA_TAG_PROTO_NONE` despite a comment about a KS8995 protocol, limiting real CPU-port tagging behavior. Global MTU bits affect all ports, so one large MTU request changes switch-wide acceptance.

Test signals: probe for each variant, reset GPIO timing, SPI command header correctness for 8-bit and 12-bit address formats, family/chip/revision rejection paths, DSA registration, CPU-port phylink speed/duplex writes, bridge learning flag toggles, STP state register programming, MTU threshold transitions at 1522/1536/1916 inclusive sizes, and remove reset assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/ks8995.c -->
