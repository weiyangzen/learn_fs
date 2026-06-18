# Research: subset-b-004429 Hisilicon HNS DSAF/HNAE files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hnae.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hnae.c

## Purpose
`hnae.c` implements the Hisilicon Network Acceleration Engine framework core. It provides a class device registry for AE providers, maps firmware nodes to registered AE devices, allocates/free rings and descriptors for consumers, owns the notifier chain for AE registration, and exports the handle lifecycle used by upper network drivers.

## Important APIs and Functions
The exported entry points are `hnae_get_handle`, `hnae_put_handle`, `hnae_ae_register`, `hnae_ae_unregister`, `hnae_register_notifier`, `hnae_unregister_notifier`, and `hnae_reinit_handle`. `hnae_get_handle` finds an AE by fwnode, calls the provider `get_handle`, installs default or caller-supplied buffer ops, initializes every queue, pins the provider module, and adds the handle to the AE handle list. `hnae_put_handle` reverses that setup, including queue teardown, provider reset/put, module put, and class-device ref release. Internally, `hnae_init_ring`, `hnae_alloc_desc`, and `hnae_alloc_buffers` construct descriptor state; `hnae_fini_ring` and `hnae_free_buffers` tear it down.

## Control Flow
AE providers register through `hnae_ae_register`, which validates mandatory ops, creates a `hnae` class child device, initializes the handle list lock, and notifies listeners with `HNAE_AE_REGISTER`. Consumers later call `hnae_get_handle`, which uses `class_find_device` and `__ae_match` against OF or ACPI fwnodes, asks the AE for a handle, initializes TX and RX rings for all queues, and then exposes the fully initialized handle. Reinitialization first frees queues, invokes the provider reset callback, then rebuilds each queue.

## State and Persistence
Persistent state is in memory only: class devices, AE handle lists protected by spinlock/RCU list helpers, per-ring descriptor arrays, descriptor control blocks, DMA mappings, and allocated RX pages. No disk persistence exists. RX rings receive page buffers during initialization; TX rings allocate descriptor memory but not packet buffers until upper layers submit packets.

## Dependencies and Integration Points
This file depends on Linux class devices, DMA mapping APIs, notifier chains, module refcounting, RCU list operations, firmware-node APIs, and `sk_buff`/page allocation helpers. It integrates with provider-specific `struct hnae_ae_ops` implementations, notably the DSAF adapter in `hns_ae_adapt.c`.

## Risks
DMA direction is inferred from ring flags, so wrong flags can map descriptors or buffers with the wrong direction. `hnae_free_desc` unmaps descriptor memory with `ring_to_dma_dir`, matching allocation here but relying on consistent flags. `hnae_reinit_handle` can leave a handle with all queues torn down if queue reinitialization fails after provider reset. The AE class match path assumes providers have valid OF or ACPI fwnode data.

## Test Signals
Useful checks include successful AE registration/unregistration, `hnae_get_handle` failure injection at descriptor/buffer allocation points, DMA mapping error handling, RX buffer refill correctness, notifier delivery on AE registration, and queue teardown without leaks under repeated handle get/put and reinit cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hnae.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hnae.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hnae.h

## Purpose
`hnae.h` defines the shared HNAE contract: descriptor layout, ring and queue state, handle state, AE device registration structures, callback tables, ring helpers, buffer operations, descriptor bit fields, coalescing constants, media/port/loopback enums, and exported framework prototypes.

## Important APIs and Types
`struct hnae_desc` is the packed hardware descriptor union for TX and RX. `struct hnae_desc_cb` is the software companion carrying DMA address, CPU buffer, private skb/page pointer, length, page offset, reuse flag, and descriptor type. `struct hnae_ring`, `struct hnae_queue`, and `struct hnae_handle` model the runtime datapath. `struct hnae_ae_ops` is the provider contract for queue setup, start/stop/reset, IRQ control, link adjustment, MAC address, multicast/unicast TCAM operations, MTU, stats, LEDs, register dumps, coalescing, pause, loopback, and RSS.

## Control Flow
The header supplies inline helpers used by the framework and netdev paths. `ring_space`, `ring_dist`, and `is_ring_empty` define ring index semantics with one unused descriptor slot. `hnae_reserve_buffer_map`, `hnae_alloc_buffer_attach`, `hnae_free_buffer_detach`, `hnae_replace_buffer`, and `hnae_reuse_buffer` provide the common RX buffer lifecycle. `hnae_reinit_all_ring_desc` and `hnae_reinit_all_ring_page_off` rewrite RX descriptor addresses after buffer-size changes.

## State and Persistence
All state is volatile kernel state. Rings persist descriptor memory, software descriptor control blocks, interrupt numbers, coalescing counters, statistics, and producer/consumer indexes for the life of a handle. Handles persist ownership, PHY/media metadata, queue array, coalescing configuration, VF and port identifiers, and buffer operation hooks.

## Dependencies and Integration Points
The header depends on Linux netdevice, PHY, ACPI, notifier, module, and device APIs. It is included by the HNAE core, the DSAF platform driver, MAC code, RCB/PPE code, and upper Ethernet driver code. Register field helper macros (`hnae_set_field`, `hnae_get_field`, etc.) mirror DSAF register helpers and are used for descriptor bit manipulation.

## Risks
The header has a duplicated `get_regs` function pointer declaration in `struct hnae_ae_ops`, which is harmless only if the compiler accepts the duplicate member in this source snapshot; in normal C this would be a build issue, so this tree likely reflects an older or transformed source state that deserves compile validation. Descriptor bit masks include a suspicious `HNS_RXD_IPOFFSET_M` definition based on `HNS_TXD_IPOFFSET_S`, so any users should be checked for intended shift values. Inline buffer replacement assumes the reserved control block is fully mapped and initialized.

## Test Signals
Compile-time coverage is important for structure layout and callback-table compatibility. Runtime signals include RX descriptor address programming after MTU changes, correct ring-space accounting under wraparound, page reuse paths, and ethtool operation availability through the AE ops table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hnae.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_ae_adapt.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_ae_adapt.c

## Purpose
`hns_ae_adapt.c` adapts the DSAF hardware implementation to the generic HNAE framework. It allocates HNAE handles from DSAF RCB ring-pair resources, translates AE operations into MAC/PPE/RCB/DSAF calls, composes stats and register dumps, and registers the DSAF AE device.

## Important APIs and Functions
`hns_dsaf_ae_init` and `hns_dsaf_ae_uninit` register/unregister the AE. The `hns_dsaf_ops` table implements HNAE callbacks: handle allocation, queue init/fini, start/stop/reset, ring IRQ toggles, link state and adjustment, MAC address management, multicast/unicast operations, MTU, TSO, pause, coalescing, promisc, stats, strings, LEDs, register dumps, and RSS. `hns_ae_get_handle` allocates `struct hnae_vf_cb`, chooses unused ring-pair blocks, and populates `struct hnae_handle` metadata from the selected MAC control block.

## Control Flow
Handle creation calculates queue and VF counts from `rcb_common[0]`, scans ring pairs for an unused VF slot, marks each ring pair used, then binds handle queues to those RCB queue objects. Start enables broadcast reception, clears TX/RX interrupts, enables all rings, waits, then starts the MAC. Stop drains TX, stops the MAC, disables rings, drains RX, and disables broadcast. Link adjustment on v2 disables MAC RX, waits for RCB/PPE/DSAF/MAC flow-down, changes link settings, then re-enables RX.

## State and Persistence
State is in the DSAF device and handle structures: ring-pair `used_by_vf` flags, VF identifiers, MAC metadata, shadow RSS key/indirection table in PPE, coalescing parameters, and accumulated hardware stats in RCB/PPE/MAC/DSAF structures. No persistent storage is used.

## Dependencies and Integration Points
This file sits between HNAE and `hns_dsaf_mac.c`, `hns_dsaf_main.c`, `hns_dsaf_ppe.*`, and `hns_dsaf_rcb.*`. It is the main integration point consumed by the upper Ethernet driver through `hnae_ae_ops`. It also adapts version-specific IRQ programming by selecting `hns_ae_toggle_ring_irq` for AE v1 and `hns_aev2_toggle_ring_irq` for AE v2.

## Risks
`hns_dsaf_ops` is a static mutable global, and `hns_dsaf_ae_init` changes its `toggle_ring_irq` pointer based on the registering device version. Mixed v1/v2 devices in one kernel could race or receive the wrong callback. `hns_ae_get_handle` only uses `rcb_common[0]`, so multi-common-device assumptions are narrow. Start/stop sequencing relies on fixed sleeps and polling. Multicast setup adds both MAC and VF inner ports, making TCAM cleanup correctness important.

## Test Signals
Probe tests should verify AE registration for v1 and v2, handle allocation exhaustion, ring-pair `used_by_vf` cleanup, start/stop under traffic, v2 link adjustment while packets are draining, RSS get/set consistency, ethtool stats/string counts, and interrupt mask behavior for both RCB versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_ae_adapt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_gmac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_gmac.c

## Purpose
`hns_dsaf_gmac.c` implements the GMAC-specific `struct mac_driver` callbacks for sub-10G HNS ports. It programs GMAC registers for enable/disable, link mode, pause, frame length, loopback, unicast matching, statistics, register dumps, and MAC address configuration.

## Important APIs and Functions
The only exported factory is `hns_gmac_config`, which allocates and fills a `struct mac_driver`. Important callbacks include `hns_gmac_init`, `hns_gmac_enable`, `hns_gmac_disable`, `hns_gmac_adjust_link`, `hns_gmac_need_adjust_link`, `hns_gmac_config_max_frame_length`, `hns_gmac_pause_frm_cfg`, `hns_gmac_set_mac_addr`, `hns_gmac_get_info`, `hns_gmac_update_stats`, `hns_gmac_get_stats`, and `hns_gmac_get_regs`.

## Control Flow
The shared MAC layer calls `hns_gmac_config` during MAC initialization. `hns_gmac_init` resets the GE port through `dsaf_dev->misc_op->ge_srst`, disables RX/TX, disables TX loop packets, configures debug-port matching, enables pad/CRC, enables mode-change support, and adjusts TX waterline to avoid half-duplex hangs. Start/stop calls later map directly to GMAC RX/TX enable bits. Link adjustment writes duplex and port-mode register fields based on 10/100/1000 speed.

## State and Persistence
Persistent state is the allocated `struct mac_driver` and cumulative counters stored in `mac_cb->hw_stats`. Hardware state is register-resident: enable bits, port mode, pause timer/enable, max frame length, station address, filter mode, and counters. Statistics are accumulated by reading hardware counters and adding them into software 64-bit fields.

## Dependencies and Integration Points
The file depends on `hns_dsaf_reg.h` register offsets and field definitions, DSAF register helper macros, `hns_dsaf_mac.h` callback types, and `misc_op` reset hooks. It integrates with `hns_dsaf_mac.c`, which treats the returned `mac_driver` as the GMAC implementation behind generic MAC APIs.

## Risks
`hns_gmac_need_adjust_link` compares `mac_cb->half_duplex == duplex`, which is subtle because `duplex` is full-duplex truth from the upper path. Incorrect interpretation could cause missed or excessive link reprogramming. Statistics are cumulative software additions of hardware register reads; if hardware counters are not clear-on-read, values may be overcounted. `hns_gmac_set_mac_addr` shifts signed `char` values unless callers provide unsigned-safe bytes. FIFO-clean polling can stall stop/link flows until timeout.

## Test Signals
Useful signals are register-dump length `ETH_GMAC_DUMP_NUM`, ethtool GMAC stats count matching `g_gmac_stats_string`, link adjust for all supported speeds, pause enable/disable, max-frame programming after MTU changes, FIFO-clean timeout handling, and station-address writes for the primary VF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_gmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_gmac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_gmac.h

## Purpose
`hns_dsaf_gmac.h` declares GMAC-specific enums and small configuration structures used by `hns_dsaf_gmac.c`. It captures the hardware's port-mode encoding, duplex encoding, port-mode snapshot fields, and register-dump size.

## Important APIs and Types
`enum hns_port_mode` maps hardware mode values for MII, RGMII, SGMII, GMII, and a 10GE SGMII-coded value. `enum hns_gmac_duplex_mdoe` defines half/full duplex values as read from GMAC hardware. `struct hns_gmac_port_mode_cfg` carries decoded register state: mode, max frame size, runt threshold, pad/CRC, autoneg, runt packet, and strip-pad settings. `ETH_GMAC_DUMP_NUM` defines the 96-register GMAC dump size.

## Control Flow
The header does not implement control flow. It supports GMAC info collection, where `hns_gmac_port_mode_get` fills `struct hns_gmac_port_mode_cfg` and `hns_gmac_get_info` translates it into generic `struct mac_info`.

## State and Persistence
No state is stored in this header. Its types describe volatile hardware configuration snapshots.

## Dependencies and Integration Points
It includes `hns_dsaf_mac.h`, so it depends on the generic MAC abstraction. It is private to the HNS DSAF driver and primarily included by `hns_dsaf_gmac.c`.

## Risks
The enum name `hns_gmac_duplex_mdoe` contains a typo but is consistently used. Hardware mode values must stay synchronized with register definitions in `hns_dsaf_reg.h`; otherwise speed reporting and link adjustment can drift from actual hardware encoding.

## Test Signals
Compile-time use by GMAC code, `ETH_GMAC_DUMP_NUM` matching the number of registers filled in `hns_gmac_get_regs`, and correct speed/duplex reporting from ethtool are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_gmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_mac.c

## Purpose
`hns_dsaf_mac.c` is the shared MAC layer for HNS DSAF ports. It discovers per-port configuration from OF/ACPI, chooses GMAC or XGMAC backends, initializes/reset ports, manages PHY attachment, MAC table entries, broadcast/multicast/unicast programming, MTU, pause, link status, LEDs, and stats/register passthrough.

## Important APIs and Functions
Public functions include `hns_mac_init`, `hns_mac_uninit`, `hns_mac_start`, `hns_mac_stop`, `hns_mac_reset`, `hns_mac_adjust_link`, `hns_mac_get_link_status`, `hns_mac_change_vf_addr`, `hns_mac_add_uc_addr`, `hns_mac_rm_uc_addr`, `hns_mac_set_multi`, `hns_mac_clr_multicast`, `hns_mac_set_mtu`, pause/autoneg helpers, stats/string/register helpers, promisc programming, LED updates, and FIFO wait. Internal configuration is handled by `hns_mac_get_cfg`, `hns_mac_get_info`, `hns_mac_init_ex`, `hns_mac_register_phy`, and `hns_mac_get_inner_port_num`.

## Control Flow
`hns_mac_init` enumerates child port nodes or falls back to legacy all-port initialization, allocates `hns_mac_cb` objects, obtains each port's PHY mode/media/syscon/PHY data, resets LEDs, chooses the register base, creates a backend driver via `hns_gmac_config` or `hns_xgmac_config`, resets and adjusts the MAC, and enables broadcast table entries. Runtime start/stop increments/decrements virtual user counts, toggles MAC RX/TX, clears link state, and resets LEDs. MAC address changes update DSAF TCAM entries and the backend station address for VM 0.

## State and Persistence
Each `hns_mac_cb` stores persistent per-port runtime state: PHY device/interface, media type, speed/duplex/link, max frame size, pause timer, CPLD/serdes regmaps, multicast mask, TCAM address indexes per VM, LED packet counters, hardware stats, and the backend `mac_driver`. The DSAF TCAM software mirror in `hns_dsaf_main.c` is mutated through calls from this layer.

## Dependencies and Integration Points
This file integrates the DSAF device with GMAC/XGMAC backends, PHY/MDIO, ACPI and OF firmware properties, syscon/regmap, CPLD LED control, RCB MTU constraints, and DSAF TCAM operations. It is called by the AE adapter for all netdev-facing operations.

## Risks
Initialization can partially create `mac_cb` objects before later ports fail; devm allocation mitigates memory leaks, but hardware/backend cleanup depends on caller unwind. `hns_mac_stop` uses a virtual-device counter and can leave hardware enabled until all users stop; incorrect balancing would hold a port open. `hns_mac_get_inner_port_num` embeds DSAF mode assumptions and queue topology, so invalid mode or VF values affect TCAM routing. ACPI PHY registration intentionally ignores missing PHY except `-EPROBE_DEFER`, which can hide platform description gaps.

## Test Signals
Probe with child-node and legacy no-child configurations, OF and ACPI paths, SGMII and XGMII ports, MTU boundary tests against buffer size and max BD count, MAC address add/remove including invalid addresses, multicast cleanup per VF, pause/autoneg behavior on v1/v2 and debug/service ports, LED updates on fiber ports, and repeated start/stop reference balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_mac.h

## Purpose
`hns_dsaf_mac.h` declares the shared MAC abstraction used by DSAF, GMAC, XGMAC, and the AE adapter. It defines MAC modes, supported capabilities, MTU limits, address classification helpers, port state, backend callback shape, stats layout, and exported MAC helper APIs.

## Important APIs and Types
Key types are `struct hns_mac_cb`, the persistent per-port control block; `struct mac_driver`, the backend callback table; `struct mac_params`, initialization input for GMAC/XGMAC backends; `struct mac_info`, generic link/pause/mode snapshot; `struct mac_hw_stats`, shared ethtool counter storage; and `struct mac_stats_string`, mapping stat names to offsets. The header declares factories `hns_gmac_config` and `hns_xgmac_config` plus the public MAC service functions consumed by the AE adapter.

## Control Flow
The header is declarative. Its callback table shows the control path: shared MAC code creates a backend driver, then uses callbacks for reset/init, enable/disable, address setting, link adjustment, loopback, MTU, pause/autoneg, stats, register dumps, promiscuous mode, and FIFO drain.

## State and Persistence
`struct hns_mac_cb` is the main state container. It persists firmware-node pointers, MMIO/regmap handles, CPLD LED state, per-VM address indexes, link/speed/duplex/MTU/pause values, media and PHY data, hardware stats, and the backend pointer. This state lives for the platform device lifetime.

## Dependencies and Integration Points
The header depends on Linux VLAN, PHY, regmap, and kernel networking types, and it includes `hns_dsaf_main.h`, forming a tight mutual dependency between DSAF and MAC types. It is included by GMAC/XGMAC implementations, misc reset/LED code, DSAF main, and AE adaptation.

## Risks
The header contains many hardware constants and address macros whose correctness is assumed throughout the driver. `MAC_IS_*` macros evaluate pointer expressions directly and should only be called with valid 6-byte Ethernet addresses. The mutual include relationship with `hns_dsaf_main.h` is fragile and relies on include guards and forward declarations.

## Test Signals
Compile checks for callback-table completeness, ethtool stat count/name alignment through `MAC_STATS_FIELD_OFF`, MTU-limit behavior using `MAC_MIN_MTU`, `MAC_MAX_MTU`, and `MAC_MAX_MTU_V2`, and capability exposure for GMAC versus XGMAC ports are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_main.c

## Purpose
`hns_dsaf_main.c` is the DSAF platform driver and hardware programming core. It parses platform configuration, maps resources, initializes DSAF fabric hardware, manages the TCAM/line MAC table software mirror, exposes DSAF stats and register dumps, controls pause/promiscuous behavior, and binds/unbinds the MAC, PPE, and AE layers.

## Important APIs and Functions
The platform entry points are `hns_dsaf_probe` and `hns_dsaf_remove`. Exported/internal service APIs include `hns_dsaf_set_mac_uc_entry`, `hns_dsaf_add_mac_mc_port`, `hns_dsaf_del_mac_entry`, `hns_dsaf_del_mac_mc_port`, `hns_dsaf_rm_mac_addr`, `hns_dsaf_clr_mac_mc_port`, `hns_dsaf_set_promisc_tcam`, `hns_dsaf_set_promisc_mode`, pause helpers, stats/string/register helpers, `hns_dsaf_fix_mac_mode`, and `hns_dsaf_wait_pkt_clean`. Hardware init is decomposed into common config, inode config, SBM config, TCAM/line init, and VOQ thresholds.

## Control Flow
Probe allocates `struct dsaf_device` plus private state, reads OF/ACPI config, initializes DSAF hardware unless in debug single-port mode, initializes MACs, initializes PPE, then registers the HNAE AE. Failure unwinds in reverse. Hardware initialization resets DSAF, programs common mode, queue IDs, STP/SW port type, interrupts, inode topology, SBM watermarks/MIB/SRAM init, TCAM/line discard defaults, and VOQ thresholds. TCAM updates are protected by `tcam_lock` and write address/data/config registers followed by pulse registers.

## State and Persistence
State is volatile. `struct dsaf_device` holds resource bases, version/mode, descriptor and buffer sizing, TCAM size, child component pointers, stats, interrupt stats, and `tcam_lock`. Private `struct dsaf_drv_priv` holds the software MAC TCAM table, where valid entries mirror hardware indexes. Hardware stats are accumulated in `hw_stats`.

## Dependencies and Integration Points
This file integrates Linux platform/OF/ACPI probing, syscon/regmap, MMIO resources, DMA mask setup, DSAF register helpers, MAC init/uninit, PPE init/uninit, RCB queue-mode helpers, misc reset operations, and HNAE AE registration. It is the foundational provider used by `hns_ae_adapt.c`.

## Risks
The TCAM software mirror and hardware can diverge if a hardware write fails because many register writes are void and not verified. Promiscuous mode reserves reverse-search TCAM entries near the end; exhaustion or failed second-stage multicast setup can leave only partial promisc state. Several waits use fixed polling limits and return `-ENODEV`/`-EBUSY` on hardware readiness failures. The config parser supports only specific mode strings in `g_dsaf_mode_match`; new firmware strings fail probe.

## Test Signals
Probe/remove on OF and ACPI systems, resource fallback ordering, invalid `desc-num`/`buf-size`/mode handling, DSAF v1/v2 init paths, TCAM add/delete for unicast/multicast/broadcast, promisc enable/disable under TCAM pressure, pause restrictions on v1, ethtool register dump count `DSAF_DUMP_REGS_NUM`, stats count v1/v2, and `hns_dsaf_wait_pkt_clean` timeout behavior should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_main.h

## Purpose
`hns_dsaf_main.h` defines the DSAF device model, operating modes, hardware table structures, stats structures, interrupt-source layouts, misc operation callbacks, private TCAM mirror entries, inline TCAM address/pulse helpers, and public DSAF service prototypes.

## Important APIs and Types
Core types include `enum dsaf_mode`, `struct dsaf_device`, `struct dsaf_misc_op`, `struct dsaf_hw_stats`, `struct hnae_vf_cb`, TCAM data/config structs, MAC single/multi destination entries, and `struct dsaf_drv_priv`. Inline helpers `hns_dsaf_tbl_tcam_addr_cfg`, `hns_dsaf_tbl_tcam_load_pul`, and `hns_dsaf_tbl_line_addr_cfg` encapsulate common table register writes. `hns_ae_get_vf_cb` maps an HNAE handle back to its DSAF VF wrapper.

## Control Flow
The header describes the layering used by implementation files: DSAF probe initializes `dsaf_device`; misc ops provide reset/LED/PHY abstraction for OF versus ACPI; MAC and AE layers call declared TCAM, stats, pause, register, and flow-drain helpers.

## State and Persistence
`struct dsaf_device` persists all driver-wide runtime state for a platform device: MMIO bases, regmap handles, version/mode, descriptor and buffer config, component arrays, misc ops, stats, interrupt status, and TCAM lock. `struct dsaf_drv_priv` persists the software MAC table allocated beside the device object.

## Dependencies and Integration Points
It includes `hnae.h`, `hns_dsaf_reg.h`, and `hns_dsaf_mac.h`, tying together the HNAE framework, register map, and MAC abstraction. The header is shared across DSAF main, MAC, misc, and AE adapter code.

## Risks
Many constants encode hardware capacities and offsets; incorrect values affect memory allocation, TCAM masks, stats sizes, and queue routing. `hnae_vf_cb` requires `ae_handle` to be the final member for flexible-array allocation assumptions. The mutual dependency with MAC headers is fragile but protected by include guards.

## Test Signals
Compile-time structure layout, TCAM port mask sizing from `DSAF_PORT_MSK_NUM`, stats count constants (`DSAF_STATIC_NUM`, `DSAF_V2_STATIC_NUM`), register dump size `DSAF_DUMP_REGS_NUM`, and correct mapping from `hnae_handle` to `hnae_vf_cb` are key validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_misc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_misc.c

## Purpose
`hns_dsaf_misc.c` provides platform-specific miscellaneous operations for DSAF: subsystem register access, CPLD/ACPI LED control, reset sequencing for DSAF/XGE/GE/PPE blocks, PHY-interface discovery, SFP presence detection, SerDes loopback programming, and platform-device lookup by fwnode.

## Important APIs and Functions
`hns_misc_op_get` allocates and fills `struct dsaf_misc_op` with either OF/MMIO/syscon callbacks or ACPI DSM callbacks. `hns_dsaf_find_platform_device` finds an associated platform device by fwnode. Internal operations include `hns_cpld_set_led`, `cpld_led_reset`, `cpld_set_led_id`, ACPI LED variants, `hns_dsaf_rst`, per-port reset functions for XGE/GE/PPE, `hns_ppe_com_srst`, `hns_mac_get_phy_if`, `hns_mac_get_sfp_prsnt`, and SerDes loopback variants.

## Control Flow
During DSAF config, `hns_misc_op_get` selects the operation table based on `dev_of_node` or ACPI fwnode. Later MAC/DSAF code invokes these callbacks for reset, LED, PHY mode, SFP presence, and loopback. OF paths write syscon/MMIO registers directly. ACPI paths package integer arguments and call `_DSM` functions identified by `hns_dsaf_acpi_dsm_guid`.

## State and Persistence
The file maintains no global mutable state beyond the static ACPI GUID. It mutates `mac_cb->cpld_led_value`, reset registers, SerDes registers, and platform hardware state through regmap/MMIO or ACPI firmware calls.

## Dependencies and Integration Points
It depends on ACPI DSM APIs, regmap/syscon helpers, platform bus lookup, DSAF register definitions, MAC control blocks, and PPE/DSAF reset semantics. It is consumed through `dsaf_dev->misc_op` by DSAF main and MAC code.

## Risks
ACPI DSM calls mostly log warnings on failure but often do not propagate errors, so hardware reset/LED operations can silently fail from higher layers. OF reset paths rely on port offsets parsed in MAC config and may no-op for out-of-range ports. SerDes loopback lane mapping is static and version-sensitive. `hns_dsaf_find_platform_device` returns a device with a reference from bus lookup; callers must be aware of lifetime expectations.

## Test Signals
OF and ACPI probe paths should verify selected callbacks, reset register writes or DSM calls for each block, LED active/inactive and link/data updates, SFP presence handling, PHY interface detection for v1/v2 and debug/service ports, SerDes loopback toggling, and error propagation for failed syscon reads/writes where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_misc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_misc.h

## Purpose
`hns_dsaf_misc.h` declares the miscellaneous DSAF support API and constants for CPLD LED control, SFP offset handling, and LED bit fields.

## Important APIs and Types
The header exposes `hns_misc_op_get(struct dsaf_device *)`, which returns a populated `struct dsaf_misc_op`, and `hns_dsaf_find_platform_device(struct fwnode_handle *)`, which supports ACPI MDIO lookup. Constants define CPLD port offsets, LED on/off values, default LED values, SFP presence register offset, and speed/link/data/anchor LED bit positions.

## Control Flow
There is no executable control flow in the header. It supports the MAC and DSAF initialization flow by making misc operation discovery and platform-device lookup available to other files.

## State and Persistence
No state is stored in the header. The constants describe fields later persisted in hardware/CPLD state and `hns_mac_cb->cpld_led_value`.

## Dependencies and Integration Points
It includes OF, OF address, platform device, and `hns_dsaf_mac.h`. It is included by DSAF main, MAC, and misc implementation code.

## Risks
The exported constants are tightly coupled to CPLD and LED wiring. Incorrect bit positions would produce misleading link/activity LEDs without affecting packet datapath tests, so board-level validation is needed.

## Test Signals
Compile-time inclusion, successful `hns_misc_op_get` selection, LED bitfield behavior through ethtool identify/link updates, and ACPI MDIO platform-device lookup are the relevant checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_misc.h -->
