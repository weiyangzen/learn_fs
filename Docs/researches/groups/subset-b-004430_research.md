# Research: subset-b-004430

This grouped report covers the requested Hisilicon HNS/HNS3 Ethernet driver files. Each section is source-tree-aligned and bounded by reconciliation markers for deterministic per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_ppe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_ppe.c

## Purpose

`hns_dsaf_ppe.c` implements initialization, reset, configuration, statistics, and register dump support for the HNS DSAF PPE blocks. PPE sits between software rings/RCB and the DSAF switching fabric, so this file programs packet parsing/checksum behavior, queue-id mode selection, RSS key and indirection state for v2 hardware, VLAN stripping, per-channel port mode, and common PPE reset sequencing.

## Important APIs, Types, And Functions

The exported entry points are `hns_ppe_init`, `hns_ppe_uninit`, `hns_ppe_reset_common`, `hns_ppe_wait_tx_fifo_clean`, `hns_ppe_update_stats`, `hns_ppe_get_sset_count`, `hns_ppe_get_regs_count`, `hns_ppe_get_regs`, `hns_ppe_get_strings`, `hns_ppe_get_stats`, `hns_ppe_set_tso_enable`, `hns_ppe_set_rss_key`, and `hns_ppe_set_indir_table`. They operate on `struct hns_ppe_cb` and `struct ppe_common_cb` declared in `hns_dsaf_ppe.h`.

Key internal helpers allocate common PPE state with `devm_kzalloc`, derive MMIO bases from `dsaf_dev->ppe_base`, initialize per-PPE channel control blocks, select `enum ppe_qid_mode` from `dsaf_dev->dsaf_mode`, toggle soft resets via `dsaf_dev->misc_op`, and mask/clear exception interrupts.

## Control Flow

`hns_ppe_init` loops over `HNS_PPE_COM_NUM`, allocates PPE common state and matching RCB common state, populates per-PPE and per-RCB ring configuration, then calls `hns_ppe_reset_common` for each common block. `hns_ppe_reset_common` resets the PPE common block, initializes each existing PPE channel only if a matching `mac_cb` exists, initializes RCB common hardware, then commits the RCB initialization. `hns_ppe_init_hw` resets a channel, disables PPE exception interrupts, chooses GE mode for debug PPEs and XGE mode for service PPEs, enables protocol checksum checking, clears counters, and for v2 disables VLAN strip, sets max frame length, programs a generated RSS key, and installs a default linear indirection table.

Runtime mutation is small and direct: RSS and TSO setters write PPEv2 registers, and `hns_ppe_wait_tx_fifo_clean` polls `PPE_CURR_TX_FIFO0_REG` until the lower FIFO count bits drain or reports `-EBUSY`.

## State And Persistence

The durable driver state is in devm-managed `ppe_common_cb` objects attached to `dsaf_dev->ppe_common[]`, per-channel `hns_ppe_cb` shadows, RSS key/indirection arrays, and cumulative software-maintained `hns_ppe_hw_stats`. Hardware register state is volatile and reconstructed during reset or open flows. `hns_ppe_update_stats` accumulates hardware counters into 64-bit software fields; it does not clear all source counters except where hardware counter-clear enable has been configured.

## Dependencies And Integration Points

This file depends on `hns_dsaf_main.h`, `hns_dsaf_mac.h`, `hns_dsaf_rcb.h`, and the register helpers/macros in `hns_dsaf_reg.h`. It integrates with RCB setup through `hns_rcb_common_get_cfg`, `hns_rcb_get_cfg`, `hns_rcb_common_init_hw`, and `hns_rcb_common_init_commit_hw`, and with ethtool through stats strings and register dump callbacks routed by higher-level AE operations.

## Risks And Test Signals

Primary risks are bad DSAF-mode to QID-mode mappings, incorrect FIFO drain timeouts during reset or close, RSS table width assumptions (`& 0x1F`), and reset ordering between PPE and RCB. Useful test signals include successful probe across service/debug modes, no `get ppe queue mode failed` or FIFO timeout logs, RSS key/indir ethtool round-trips on v2 hardware, stable packet distribution after reset, and sane PPE counters in `ethtool -S` and register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_ppe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_ppe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_ppe.h

## Purpose

`hns_dsaf_ppe.h` defines the public PPE contract for the HNS DSAF Ethernet driver. It describes PPE topology constants, RSS sizing, dump/stat counts, queue-id and port modes, common block modes, statistics storage, and the control-block layout consumed by `hns_dsaf_ppe.c`, RCB, MAC, and AE integration code.

## Important APIs, Types, And Functions

Important constants include `HNS_PPE_SERVICE_NW_ENGINE_NUM`, `HNS_PPE_DEBUG_NW_ENGINE_NUM`, `HNS_PPE_COM_NUM`, `PPE_COMMON_REG_OFFSET`, `PPE_REG_OFFSET`, `ETH_PPE_DUMP_NUM`, `ETH_PPE_STATIC_NUM`, `HNS_PPEV2_RSS_IND_TBL_SIZE`, `HNS_PPEV2_RSS_KEY_SIZE`, `HNS_PPEV2_RSS_KEY_NUM`, and `HNS_PPEV2_MAX_FRAME_LEN`.

`enum ppe_qid_mode` maps SoC DSAF modes to PPE queue-id interpretation. `enum ppe_port_mode` distinguishes GE and XGE PPE channel modes, while `enum ppe_common_mode` distinguishes debug and service common blocks. `struct hns_ppe_hw_stats` stores cumulative RX/TX PPE counters. `struct hns_ppe_cb` contains the per-channel device pointer, common backpointer, hardware stats, index, MMIO base, IRQ placeholder, RSS indirection shadow, and RSS key shadow. `struct ppe_common_cb` stores the dev/device pointers, common MMIO base, mode, index, channel count, and flexible array of `hns_ppe_cb`.

The prototypes expose PPE initialization, reset, uninitialization, FIFO drain, stats, registers, strings, TSO, RSS key, and RSS indirection programming.

## Control Flow

This header itself contains no executable control flow, but it shapes PPE lifecycle calls. Higher layers allocate a `ppe_common_cb` sized with `struct_size(..., ppe_cb, ppe_num)`, call `hns_ppe_init` during DSAF initialization, use the RSS/TSO setters when netdev or ethtool features change, call stats and register helpers through AE callbacks, and call `hns_ppe_uninit` or `hns_ppe_reset_common` during device teardown or reset.

## State And Persistence

State represented here is entirely in memory and MMIO-backed. The RSS key and indirection table arrays are driver shadows for v2 hardware state. `hns_ppe_hw_stats` persists cumulative counter snapshots for the life of the control block but is lost across driver unload.

## Dependencies And Integration Points

The header includes Linux platform-device types and HNS DSAF headers for `struct dsaf_device`, MAC control blocks, and RCB APIs. It is included by PPE implementation code and by other DSAF code that needs PPE reset, stats, or feature toggles.

## Risks And Test Signals

The main risks are ABI drift between constants and hardware register dump layout, flexible-array allocation mistakes, and mismatched RSS sizing versus ethtool or PPEv2 hardware. Test signals are successful compile-time integration, no out-of-bounds register dump accesses for `ETH_PPE_DUMP_NUM`, valid `ethtool -x/-X` behavior on v2 hardware, and matching stat-string count to `ETH_PPE_STATIC_NUM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_ppe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_rcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_rcb.c

## Purpose

`hns_dsaf_rcb.c` implements the HNS RCB ring-control block used by the netdev data path. It maps DSAF modes to queue/ring topology, allocates and initializes per-ring hardware descriptors, configures interrupt coalescing, resets rings, polls ring emptiness during reset, controls ring interrupts, exposes hardware/software stats, and supplies register dump support.

## Important APIs, Types, And Functions

The exported API includes ring wait/reset/control functions (`hns_rcb_wait_fbd_clean`, `hns_rcb_wait_tx_ring_clean`, `hns_rcb_reset_ring_hw`, `hns_rcb_ring_enable_hw`, interrupt clear/mask variants for v1/v2), common setup (`hns_rcb_common_get_cfg`, `hns_rcb_common_free_cfg`, `hns_rcb_common_init_hw`, `hns_rcb_common_init_commit_hw`, `hns_rcb_get_cfg`, `hns_rcb_get_queue_mode`), coalescing getters/setters, buffer-size programming, stats accessors, and register-dump helpers.

Internally it uses `struct rcb_common_cb`, `struct ring_pair_cb`, `struct hnae_queue`, and `struct hnae_ring`. It relies on RCB register offsets and bit fields from `hns_dsaf_reg.h`.

## Control Flow

Configuration starts with `hns_rcb_common_get_cfg`, which determines ring count from `dsaf_dev->dsaf_mode`, allocates a flexible-array `rcb_common_cb`, stores descriptor count, queue mode limits, virtual/physical common MMIO bases, and attaches it to `dsaf_dev->rcb_common[]`. `hns_rcb_get_cfg` iterates each ring, calculates ring MMIO base and physical base, derives the port inside the common block, obtains TX/RX IRQs from the platform device using different v1/v2 layouts, and initializes TX/RX ring software fields.

Hardware initialization in `hns_rcb_common_init_hw` clears/masks common exception interrupts, verifies the hardware init flag, writes per-port descriptor counts, default coalescing frames/timeouts, endian mode, and v1/v2 FNA/FA/TSO mode bits. `hns_rcb_common_init_commit_hw` uses write memory barriers around the system-finish register write.

At runtime, ring reset waits for TX fetched descriptors to drain, disables prefetch, toggles reset, and polls whether the ring can be reset. Interrupt helpers write per-ring mask/status registers. Coalescing setters validate ranges and hardware limits before writing common registers. Stats routines combine RCB packet records, PPE queue counters, and software ring stats.

## State And Persistence

Persistent driver state lives in `rcb_common_cb` and each `ring_pair_cb`. Hardware state lives in descriptor base registers, descriptor count/length registers, ring head/tail/fbd counters, prefetch enable, interrupt masks/status, common endian and TSO bits, and coalescing registers. Software stats in `hns_ring_hw_stats` are cumulative until control-block teardown.

## Dependencies And Integration Points

RCB is initialized through PPE setup and consumed by `hns_enet.c` for TX/RX DMA rings, IRQ handling, and NAPI. It also feeds ethtool stats and register dumps through AE operations. It integrates with platform IRQ resources, DSAF mode/version helpers, and `hnae` queue/ring abstractions.

## Risks And Test Signals

Risks include invalid IRQ indexing between v1 and v2, bad DSAF mode topology resulting in incorrect port/ring mapping, coalescing values outside hardware ranges, reset loops that leave prefetch disabled or rings uncleared, and stats races with live traffic. Test signals include successful probe with expected queue count, no `wait fbd clean fail`, `head not equal to tail`, or `reset ring fail` logs, functioning TX/RX after reset, correct interrupt moderation from `ethtool -c/-C`, and coherent ring register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_rcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_rcb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_rcb.h

## Purpose

`hns_dsaf_rcb.h` declares RCB topology constants, interrupt flags, ring/common control blocks, stats structures, and public RCB APIs used by the HNS DSAF and netdev layers. It is the shared contract between low-level RCB hardware programming and the Ethernet data path.

## Important APIs, Types, And Functions

Important constants describe IRQ layout, ring offset, service/debug engine count, descriptor limits, MTU limit, pending descriptor bounds, coalescing limits/defaults, buffer-size encodings, dump sizes, and TSO mode encodings. `enum rcb_int_flag` defines TX and RX interrupt flags. `struct hns_ring_hw_stats` stores RCB/PPE packet counters for a ring pair. `struct ring_pair_cb` binds one `hnae_queue` to common RCB state, device, global index, buffer size, TX/RX IRQs, port id, VF usage marker, and hardware stats. `struct rcb_common_cb` stores common MMIO/physical bases, DSAF device, VM/queue limits, common index, ring count, descriptor count, and the flexible ring-pair array.

The function declarations cover allocation/configuration, hardware init/commit, interrupt control, ring reset, descriptor drain waits, coalescing accessors, stats, register dumps, strings, and RX/TX buffer-size programming.

## Control Flow

No code executes in this header. Its layout drives RCB lifecycle: DSAF/PPE code allocates common blocks, netdev code consumes `hnae_queue` ring fields, ethtool queries use the stats/register functions, and reset paths call drain/reset helpers. The header also keeps v1/v2 differences visible through constants such as `HNS_RCB_RING_MAX_TXBD_PER_PKT` and `HNS_RCBV2_RING_MAX_TXBD_PER_PKT`.

## State And Persistence

The structures here hold in-memory topology and cumulative stats for a device instance. `io_base` and `phy_base` connect those objects to MMIO and DMA-visible addresses, while `desc_num`, `ring_num`, `max_vfn`, and `max_q_per_vf` persist the DSAF-mode-derived topology until device teardown.

## Dependencies And Integration Points

The header includes Linux netdevice/platform-device types plus `hnae.h` and `hns_dsaf_main.h`. It is included by PPE, RCB implementation, and netdev code. It is tightly coupled to `hnae_queue` and `hnae_ring` layout because `ring_pair_cb` embeds a queue.

## Risks And Test Signals

Risks include structure layout drift from `hnae`, incorrect dump/stat count constants, and callers passing unsupported buffer sizes to `hns_rcb_buf_size2type`. Test signals are clean builds across hardware-version configs, ethtool stat count consistency, queue count within `NIC_MAX_Q_PER_VF`, and no ring allocation or IRQ setup failures during probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_rcb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_reg.h

## Purpose

`hns_dsaf_reg.h` is the central register-map and MMIO helper header for the HNS DSAF, PPE, RCB, GMAC, and XGMAC blocks. It names topology limits, register offsets, bit fields, masks, and small inline helpers used throughout the Hisilicon HNS driver.

## Important APIs, Types, And Functions

The file groups definitions for DSAF topology (`DSAF_MAX_PORT_NUM`, `DSAF_SERVICE_NW_NUM`, `DSAF_TOTAL_QUEUE_NUM`, TCAM/line counts), subsystem clock/reset/status registers, SerDes/HILINK registers, DSAF core SRAM/config/interrupt/stat registers, inode/SBM/XOD/VOQ/table registers, PPE common/channel/RSS registers, RCB common/ring registers, GMAC registers, XGMAC registers and 64-bit stat offsets, and bit-field masks for DSAF, PPE, RCB, GMAC, and XGMAC controls.

The helper API consists of `dsaf_write_reg`, `dsaf_read_reg`, `dsaf_write_syscon`, `dsaf_read_syscon`, `dsaf_set_reg_field`, `dsaf_get_reg_field`, `dsaf_write_b`, `dsaf_read_b`, `hns_mac_reg_read64`, and macros such as `dsaf_write_dev`, `dsaf_read_dev`, `dsaf_set_field`, `dsaf_set_bit`, `dsaf_get_field`, `dsaf_get_bit`, `dsaf_set_dev_field`, `dsaf_set_dev_bit`, `dsaf_get_dev_field`, and `dsaf_get_dev_bit`.

## Control Flow

This header is mostly declarative, but its inline helpers define the common read-modify-write pattern for register fields. Callers pass a control block with `io_base`; `dsaf_*_dev` macros offset into that base. Field macros mask and shift values consistently before writeback. The `hns_mac_reg_read64` macro reads XGMAC 64-bit MIB counters from the MAC stats region.

## State And Persistence

The file itself holds no runtime state. Its constants define how runtime state is persisted in device registers. Because many register values control reset, clock, interrupt masks, descriptor bases, queues, MAC enablement, pause, counters, and table entries, correctness of these constants directly governs hardware behavior and diagnostics.

## Dependencies And Integration Points

It includes `<linux/regmap.h>` for syscon access and is consumed by DSAF main, PPE, RCB, GMAC, and XGMAC implementation files. It provides the shared ABI between driver code and hardware manuals, and it underpins ethtool register dumps produced by several blocks.

## Risks And Test Signals

Risks are high because a wrong offset, mask, or shift can silently program unrelated hardware state. Special attention is needed around v1/v2 alternate registers, 64-bit `1ULL` masks narrowed into 32-bit registers, register dump array sizes, and read-modify-write races when hardware also updates bits. Test signals include successful probe/reset on each supported SoC revision, accurate ethtool register dumps, no unexpected interrupt storms, valid RSS/RCB/PPE/XGMAC behavior, and hardware manual review for every changed offset or bit field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_xgmac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_xgmac.c

## Purpose

`hns_dsaf_xgmac.c` implements the 10G XGMAC MAC-driver backend for HNS. It supplies the `struct mac_driver` callbacks used by the DSAF MAC abstraction to reset, enable/disable, configure pause and frame behavior, query link and MAC info, collect XGMAC MIB counters, and dump XGMAC registers.

## Important APIs, Types, And Functions

The public constructor is `hns_xgmac_config`, which allocates a `struct mac_driver` and populates callback pointers. Internal helpers include TX/RX enable setters, LF/RF insertion control, PMA FEC enable, interrupt clear/mask, initialization/reset/free, pad/CRC configuration, pause frame configuration, pause MAC address programming, TX pause-time programming, max frame length programming, stats update/get/string/count helpers, link/status/info getters, and register dump routines.

The static `g_xgmac_stats_string` table maps ethtool stat names to `struct mac_hw_stats` offsets via `MAC_STATS_FIELD_OFF`.

## Control Flow

`hns_xgmac_config` is called with `hns_mac_cb` and `mac_params`, allocates a devm-managed driver, assigns IDs, mode, base address, device and MAC callback, then installs all XGMAC-specific operations. `hns_xgmac_init` toggles XGE soft reset through `dsaf_dev->misc_op`, initializes LF/RF control, clears and masks exceptions, disables FEC, and disables TX/RX. Enable/disable callbacks toggle `XGMAC_MAC_ENABLE_REG` bits and manage LF insertion state.

Stats flow is two-stage: `hns_xgmac_update_stats` reads each 64-bit XGMAC MIB register into `mac_cb->hw_stats`; `hns_xgmac_get_stats` copies fields into ethtool buffers according to the static descriptor table. Register dump reads base config, MAC, PCS, PMA, and MIB counters into a fixed 214-register array with sentinel values at the end.

## State And Persistence

XGMAC state lives primarily in hardware registers. The `mac_driver` stores static driver pointers and the MMIO base. `mac_cb->hw_stats` stores the latest sampled 64-bit counters. Pause configuration, max frame length, LF/RF insert mode, FEC, TX/RX enablement, and control bits are volatile and reinitialized on reset.

## Dependencies And Integration Points

The file depends on Linux 64-bit MMIO read support, OF MDIO headers, `hns_dsaf_main.h`, `hns_dsaf_mac.h`, `hns_dsaf_xgmac.h`, and `hns_dsaf_reg.h`. It integrates with DSAF MAC selection, ethtool stats/register callbacks, link-status reporting, pause controls, and netdev MTU/pause operations through the generic AE/MAC callback layer.

## Risks And Test Signals

Risks include missing support for autoneg/loopback callbacks in this backend, incorrect signed `char` handling when constructing pause MAC registers, stale stats if update is not called before get, and register dump count mismatches. Test signals include stable 10G link up/down reporting, correct pause enable state from ethtool, traffic counters matching hardware expectations, no XGMAC exception interrupt storms, successful reset/reopen, and valid 214-register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_xgmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_xgmac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_xgmac.h

## Purpose

`hns_dsaf_xgmac.h` is the small public constant header for the XGMAC backend. It defines the ethtool register dump length and the LF/RF insert mode values used when enabling or disabling the XGMAC port.

## Important APIs, Types, And Functions

The header defines `HNS_XGMAC_DUMP_NUM` as 214, `HNS_XGMAC_NO_LF_RF_INSERT` as `0x0`, and `HNS_XGMAC_LF_INSERT` as `0x2`. It declares no structs or functions.

## Control Flow

The header has no executable control flow. `hns_dsaf_xgmac.c` uses the LF/RF constants in its enable/disable callbacks and uses `HNS_XGMAC_DUMP_NUM` in `hns_xgmac_get_regs_count`.

## State And Persistence

There is no runtime state in the header. Its constants constrain register dump buffer sizing and XGMAC link-fault signaling behavior.

## Dependencies And Integration Points

This header is included by the XGMAC implementation. The values must stay synchronized with the XGMAC register definitions in `hns_dsaf_reg.h` and with ethtool register dump consumers.

## Risks And Test Signals

Risks are limited but important: a wrong dump count can cause truncated or overrun register dumps, and a wrong LF insert code can affect link-fault signaling during MAC disable. Test signals include correct `ethtool -d` length and expected LF behavior when the port is administratively disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_xgmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_enet.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_enet.c

## Purpose

`hns_enet.c` is the HNS net_device driver. It bridges Linux networking APIs to the HNAE/DSAF hardware abstraction, manages platform probe/remove, queue/ring and IRQ/NAPI lifecycle, TX descriptor submission, RX buffer recycling and GRO delivery, link and PHY handling, reset/service work, MTU and feature changes, multicast/unicast filtering, statistics, and v1/v2 hardware differences.

## Important APIs, Types, And Functions

Externally visible functions are `hns_nic_net_xmit_hw`, `hns_nic_init_phy`, `hns_nic_net_reset`, and `hns_nic_net_reinit`; the module registers `hns_nic_dev_driver`. The file defines descriptor fill variants for v1 and v2/TSO, TX stop logic, RX descriptor parsing, checksum marking, page reuse, ring polling, adaptive interrupt coalescing, IRQ handler, PHY link adjustment, IRQ affinity setup, open/stop/up/down flows, loopback/MTU cleanup helpers, feature filtering, address-list syncing, stats64, queue selection, service timer/work, AE notifier integration, and platform probe/remove.

## Control Flow

Probe allocates a multiqueue Ethernet device, reads OF/ACPI configuration and the AE handle reference, maps old/new port-id properties, initializes a MAC address, sets netdev/ethtool ops and feature flags, sets DMA mask, initializes service timer/work and state bits, then tries to acquire an HNAE handle. If the handle is not ready, a notifier retries later. Handle acquisition initializes PHY, ring data, version-specific descriptor ops, and registers the netdev.

Open sets real queue counts and calls `hns_nic_net_up`. Up requests IRQs for each TX/RX ring, enables NAPI and IRQs, programs the MAC address, starts AE hardware, starts PHY, clears DOWN state, and arms the service timer. Down stops timer, queues, carrier, PHY, AE hardware, disables rings/NAPI/IRQs, and reclaims TX buffers.

TX maps the skb head and fragments, fills descriptors, updates queue accounting/stats, commits descriptors with `wmb`, and submits to hardware. Mapping failure unwinds descriptors and DMA maps. RX NAPI reads fetched descriptor count, builds skbs from copied head plus page frags, validates buffer count and descriptor flags, marks checksum unnecessary when hardware protocol/error bits allow, delivers via GRO, and replenishes RX buffers. TX NAPI reclaims completed descriptors and wakes queues when ring space recovers.

Service work handles reset requests, XGMII link polling, LED updates, and stats updates. TX timeout sets a reset-request bit and schedules service work. MTU change may stop/reopen the device and, for v2 crossing the 2048-buffer threshold, reinitializes descriptors, clears fetched RX packets through a serdes-loopback drain helper, and resets page offsets before applying the new MTU.

## State And Persistence

`struct hns_nic_priv` holds the device fwnode, HNS version, port id, PHY mode, LED state, netdev/device pointers, HNAE handle, version-specific ops, ring-data array, cached link state, TX timeout counter, state bits, service timer, work item, and notifier. Ring state lives in `hnae_ring` descriptor arrays, DMA mappings, producer/consumer indexes, per-ring stats, and NAPI objects. Hardware state is reestablished during open/reset.

## Dependencies And Integration Points

The driver depends on the Linux netdev, NAPI, IRQ, DMA, PHY, OF/ACPI, VLAN, checksum, and platform-driver APIs. It integrates heavily with `hnae` handles and AE ops for start/stop, queue transmit, ring IRQ toggles, MAC/link/MTU/RSS/coalesce operations, LED/status/stats, and handle registration. `hns_ethtool_set_ops` attaches user-facing diagnostics.

## Risks And Test Signals

Major risks are DMA unwind correctness, descriptor count validation, ring index wraparound, queue stop/wake memory ordering, adaptive coalescing races across rings, reset/reinit state-bit deadlocks, MTU transitions while packets are fetched, PHY/link adjustments during traffic, and notifier/remove ordering. Test signals include probe/remove under OF and ACPI, sustained TX/RX with checksum/GSO/GRO, queue recovery after `NETDEV_TX_BUSY`, NAPI completion without interrupt loss, TX timeout reset recovery, MTU changes across 2048-byte RX buffer threshold, multicast/promisc/UC filtering, stats64 consistency, and no DMA mapping leak warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_enet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_enet.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_enet.h

## Purpose

`hns_enet.h` declares the shared netdev-private structures, state bits, per-ring NAPI wrapper, version-specific descriptor operation hooks, and exported helper prototypes for the HNS Ethernet driver.

## Important APIs, Types, And Functions

`enum hns_nic_state` defines serialized driver state and service flags: testing, resetting, reinitializing, down, disabled, removing, service initialized/scheduled, and reset requested. `struct hns_nic_ring_data` binds one `hnae_ring` to a NAPI object, IRQ affinity mask, queue index, poll callback, optional packet post-processing callback, and completion callback. `struct hns_nic_ops` abstracts descriptor fill, TX stop checks, and RX buffer-count parsing across hardware versions. `struct hns_nic_priv` is the netdev private state, carrying firmware node, version, port/PHY data, netdev/device, AE handle, ops, ring-data array, link cache, timeout count, state bits, service timer/work, and HNAE notifier.

Macros `tx_ring_data` and `rx_ring_data` index the split ring-data array. Exported prototypes include ethtool setup, reset/reinit, PHY init, and raw TX submission used by loopback tests.

## Control Flow

The header has no executable control flow, but it defines the object model used by `hns_enet.c` and `hns_ethtool.c`. TX rings occupy the first half of `ring_data`; RX rings occupy the second half. Version-specific callbacks are installed during AE handle acquisition and then used by the TX/RX data path.

## State And Persistence

All persistent netdev instance state is represented by `hns_nic_priv`. The `state` bitmap gates lifecycle concurrency, self-tests, resets, and service scheduling. `phy_led_val` stores LED state during identify operations. `link` caches most recent link state for ethtool and service polling.

## Dependencies And Integration Points

The header includes netdevice, firmware-node network helpers, MDIO/PHY, timer, workqueue, and `hnae.h`. It is shared by the netdev implementation and ethtool implementation, so structure fields must remain consistent across both files.

## Risks And Test Signals

Risks include incorrect ring-data indexing, state-bit misuse that blocks open/close/reset, and mismatched callback signatures between versions. Test signals include successful compile, correct TX/RX queue counts, ethtool self-test access to `hns_nic_net_xmit_hw`, and clean reset/service behavior under concurrent timeout, close, and remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_enet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_ethtool.c

## Purpose

`hns_ethtool.c` implements the ethtool interface for the HNS netdev driver. It exposes link settings, driver info, ring and pause parameters, interrupt coalescing, channels, self-tests, stats, strings, LED identification, register dumps, autoneg restart, RSS get/set, and RX ring count.

## Important APIs, Types, And Functions

The only exported function is `hns_ethtool_set_ops`, which assigns a static `struct ethtool_ops`. Important helpers include `hns_nic_get_link`, `hns_get_mdix_mode`, get/set link ksettings, loopback setup/up/run/down helpers, `hns_nic_self_test`, driver info, ringparam, pause get/set, coalesce get/set, channels, ethtool stats and strings, string-set count, PHY LED state handling, register dump accessors, nway reset, RSS key/indir sizing, RSS get/set, and RX ring count.

## Control Flow

Link queries combine cached driver link, PHY status, and AE `get_status`. Link setting validates interface mode: XGMII only allows fixed 10G full duplex without autoneg, SGMII delegates to PHY when present or validates 10/100/1000 speeds otherwise, then calls AE `adjust_link` if available.

Offline self-test sets the testing state, closes the device if running, iterates supported MAC/SerDes/PHY loopback modes, resets hardware, enables loopback, starts hardware, adjusts link, transmits a crafted skb through ring 0, polls RX/TX rings manually, records failures, disables loopback, resets, clears testing, and reopens if needed. Online tests are not actively run.

Stats flow updates AE stats, copies standard rtnl stats plus timeout count, then appends AE-specific stats. String flow mirrors that layout: standard netdev names first, then AE strings. Coalescing requires equal TX/RX usecs, optionally toggles adaptive coalescing, and delegates usec/frame programming to AE ops. RSS is rejected on v1 and delegated to AE ops on newer hardware, with only no-change or Toeplitz hash function accepted.

## State And Persistence

This file mutates netdev private state only for testing flags, adaptive coalesce enable, and stored PHY LED value. Most persistent settings are delegated to PHY or AE hardware ops: link mode, pause, coalesce, RSS, LED state, and loopback. It reads counters from netdev, rings, PPE/RCB/MAC via AE callbacks.

## Dependencies And Integration Points

It depends on Linux ethtool, PHY/MDIO, netdev stats, and the HNS private structures from `hns_enet.h`. It is a user-facing facade over `hnae_ae_ops`, `hns_nic_net_reset`, `hns_nic_net_xmit_hw`, and PHY helpers.

## Risks And Test Signals

Risks include PHY page not restored after MDIX/LED operations on errors, self-test interactions with live close/open and reset, RSS operation calls without validating optional AE ops, stale or mismatched stat/string counts, and strict coalesce validation rejecting useful asymmetric settings. Test signals include `ethtool -i`, `-k`, `-S`, `-d`, `-c/-C`, `-a/-A`, `-l`, `-t offline`, `-x/-X`, physical identify LED behavior, link setting validation, and no test-state leakage after failed loopback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/Makefile

## Purpose

The HNS3 `Makefile` defines how the Hisilicon HNS3 Ethernet driver family is compiled under Kbuild. It wires include paths and object composition for the shared HNAE3 framework, the netdev-facing HNS3 driver, PF driver, VF driver, shared command/RSS/TQP-stat code, optional DCB support, devlink, debugfs, PTP, MDIO, mailbox, and error handling components.

## Important APIs, Types, And Functions

This is build metadata, not C API code. It sets `ccflags-y` to include the root HNS3 directory plus `hns3pf`, `hns3vf`, and `hns3_common`. It builds `hnae3.o` under `CONFIG_HNS3`, `hns3.o` under `CONFIG_HNS3_ENET`, `hclgevf.o` and `hclge-common.o` under `CONFIG_HNS3_HCLGEVF`, and `hclge.o` plus `hclge-common.o` under `CONFIG_HNS3_HCLGE`. Optional `CONFIG_HNS3_DCB` adds DCB objects to netdev and PF builds.

## Control Flow

Kbuild evaluates the `obj-*` lines according to kernel configuration. Composite object variables such as `hns3-objs`, `hclge-common-objs`, `hclgevf-objs`, and `hclge-objs` determine link order inside each module or built-in object. Shared `hclge-common` code is linked for both PF and VF configurations.

## State And Persistence

The file persists build relationships only. It does not create runtime state, but it controls which runtime modules and symbols exist in a configured kernel.

## Dependencies And Integration Points

It integrates with Kbuild, HNS3 PF/VF/common source trees, `CONFIG_HNS3`, `CONFIG_HNS3_ENET`, `CONFIG_HNS3_HCLGEVF`, `CONFIG_HNS3_HCLGE`, and `CONFIG_HNS3_DCB`. The include paths allow subdirectory sources to include shared headers without relative include noise.

## Risks And Test Signals

Risks include missing objects when new source files are added, duplicate inclusion of shared common objects, link-order problems for symbol dependencies, and trailing-line formatting around the long `hclge-objs` list. Test signals include all relevant config combinations building as module and built-in, `modpost` without unresolved symbols, and PF/VF modules loading with the expected dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hclge_mbx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hclge_mbx.h

## Purpose

`hclge_mbx.h` defines the HNS3 PF/VF and firmware mailbox protocol structures, opcodes, subcodes, message limits, async-response ring, and helper pointer-move macros. It is the shared protocol ABI for commands such as reset, MAC/VLAN filtering, queue/vector mapping, RSS, link status, base config, MTU, queue reset, keepalive, media type, VF table handling, and M7 firmware notifications.

## Important APIs, Types, And Functions

`enum HCLGE_MBX_OPCODE` enumerates VF-to-PF, PF-to-VF, and M7-to-PF message codes. Subcode enums define MAC/VLAN operations and table operations. Size constants include `HCLGE_MBX_MAX_MSG_SIZE`, `HCLGE_MBX_MAX_RESP_DATA_SIZE`, `HCLGE_MBX_MAX_RING_CHAIN_PARAM_NUM`, scheduler/reset timeouts, ARQ message size/count, opcode max, and push-link-status enable bit.

Important structs include `hclge_ring_chain_param`, `hclge_basic_info`, `hclgevf_mbx_resp_status`, `hclge_respond_to_vf_msg`, `hclge_vf_to_pf_msg`, `hclge_pf_to_vf_msg`, command descriptors for VF-to-PF and PF-to-VF mailbox commands, VF reset command, packed payloads for link status/mode, port base VLAN, queue info/depth, VLAN filter, MTU info, `hclgevf_mbx_arq_ring`, and `hclge_mbx_ops_param`. `hclge_mbx_ops_fn` is the PF operation callback signature.

## Control Flow

The header has no executable functions, but the protocol flow is explicit. A VF sends `hclge_mbx_vf_to_pf_cmd` with opcode/subcode/data and optional response request; PF handlers receive it through a `hclge_mbx_ops_fn`, fill `hclge_respond_to_vf_msg`, and send `hclge_mbx_pf_to_vf_cmd`. Asynchronous PF messages are queued in the VF ARQ ring, whose head/tail macros wrap modulo `HCLGE_MBX_MAX_ARQ_MSG_NUM`. Response matching uses mutex-protected `hclgevf_mbx_resp_status`, `origin_mbx_msg`, `match_id`, status, and additional data.

## State And Persistence

Mailbox state is transient command/response data plus VF-side response status and async ring indices/count. The ABI structures are packed where firmware byte layout matters. Persistent configuration affected by these messages lives elsewhere in PF/VF device state and hardware tables.

## Dependencies And Integration Points

The header includes Linux init, mutex, and types headers and forward-declares PF/VF device types. It is consumed by HNS3 PF mailbox, VF mailbox, reset, link, RSS, VLAN, MAC, queue-vector, and keepalive code. It also bridges firmware-originated M7 notifications to PF logic.

## Risks And Test Signals

Risks include ABI/layout drift, endian mistakes in `__le16/__le32/__le64` fields, opcode/subcode mismatch between PF and VF, async ring overflow, response match-id races, and insufficient validation of `msg_len`. Test signals include PF/VF mailbox negotiation, VF reset and FLR flows, MAC/VLAN/RSS/MTU operations from VF, async link status delivery, keepalive handling, ARQ wraparound, and sparse/endian checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hclge_mbx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hnae3.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hnae3.c

## Purpose

`hnae3.c` implements the HNAE3 framework registry that binds acceleration-engine devices, acceleration-engine algorithms, and clients such as the kernel NIC and RoCE clients. It serializes registration/unregistration, initializes matching AE devices, instantiates/uninstantiates clients, and coordinates unload ordering.

## Important APIs, Types, And Functions

The file owns three global lists: `hnae3_ae_algo_list`, `hnae3_client_list`, and `hnae3_ae_dev_list`. It exports `hnae3_unregister_ae_algo_prepare`, `hnae3_acquire_unload_lock`, `hnae3_release_unload_lock`, `hnae3_set_client_init_flag`, `hnae3_register_client`, `hnae3_unregister_client`, `hnae3_register_ae_algo`, `hnae3_unregister_ae_algo`, `hnae3_register_ae_dev`, and `hnae3_unregister_ae_dev`.

Internal helpers include `hnae3_client_match`, `hnae3_get_client_init_flag`, `hnae3_init_client_instance`, and `hnae3_uninit_client_instance`. The framework relies on `struct hnae3_client`, `struct hnae3_ae_dev`, `struct hnae3_ae_algo`, PCI ID matching, AE ops such as `init_ae_dev`, `uninit_ae_dev`, `init_client_instance`, and `uninit_client_instance`, and flag bits such as `HNAE3_DEV_INITED_B`, `HNAE3_KNIC_CLIENT_INITED_B`, and `HNAE3_ROCE_CLIENT_INITED_B`.

## Control Flow

Client registration validates uniqueness by client type, adds the client, then attempts to initialize it on all already-initialized matching AE devices. Client unregistration verifies existence, uninitializes the client on each matching initialized AE device, and removes it from the list.

AE algorithm registration adds the algorithm, scans existing AE devices, matches PCI IDs, assigns ops, initializes the AE device, marks it initialized, then initializes every registered client on it. AE algorithm unregistration scans initialized matching devices, uninitializes all clients, uninitializes the AE device, clears init state and ops, then removes the algorithm.

AE device registration adds the device, scans existing algorithms for a matching PCI ID, initializes the AE device through the first matching algorithm, marks it initialized, then initializes all registered clients. If algorithm init fails, the device is removed from the list. AE device unregistration uninitializes clients and AE state for any matching initialized algorithm, clears ops, and removes the device.

`hnae3_unregister_ae_algo_prepare` is a pre-unregister hook that disables SR-IOV on initialized matching PCI devices under the PCI device lock when PCI IOV is enabled.

## State And Persistence

State is global and in-memory: the three lists, `hnae3_common_lock` protecting registry updates, `hnae3_unload_lock` serializing driver unloads, per-device ops pointer, and per-device init/client bits. There is no persistent storage across module unload.

## Dependencies And Integration Points

The framework depends on Linux list/mutex/PCI APIs and `hnae3.h`. It is the rendezvous point for HNS3 PF/VF AE algorithms and upper clients. It exports symbols so separate modules can register in any order while still matching already-registered peers.

## Risks And Test Signals

Risks include duplicate AE algorithm registration not being checked by name, partial client initialization failures being logged but not rolled back globally, ordering issues when unregistering while clients or devices are probing, SR-IOV disable side effects during algorithm removal, and reliance on clients setting/clearing init flags consistently. Test signals include module load/unload in every order, PF/VF probe after client-first and device-first registration, RoCE and KNIC coexistence, SR-IOV enabled removal, no stale list nodes after failure paths, and lockdep-clean unload serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hnae3.c -->
