# subset-b-004392 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_main.c

## Purpose
`nicvf_main.c` is the PCI/netdev front end for the Cavium ThunderX NIC virtual-function driver. It binds supported Thunder NIC VF PCI IDs, negotiates VF identity and resources with the physical-function driver over a mailbox, registers the Linux `net_device`, owns open/stop/probe/remove lifecycle, and coordinates NAPI, MSI-X interrupts, RSS, XDP, timestamping, multicast receive mode, link state, and statistics.

## Important APIs, Types, and Functions
The file exports low-level register access helpers (`nicvf_reg_read`, `nicvf_reg_write`, `nicvf_queue_reg_read`, `nicvf_queue_reg_write`) and the PF mailbox API `nicvf_send_msg_to_pf`. `nicvf_open` and `nicvf_stop` are the core netdev lifecycle functions; `nicvf_xmit` is `ndo_start_xmit`; `nicvf_probe`, `nicvf_remove`, and `nicvf_shutdown` implement PCI lifecycle. NAPI and interrupt paths are centered on `nicvf_poll`, `nicvf_cq_intr_handler`, `nicvf_intr_handler`, `nicvf_misc_intr_handler`, `nicvf_rbdr_intr_handler`, and `nicvf_qs_err_intr_handler`. Feature-control entry points include `nicvf_change_mtu`, `nicvf_set_mac_address`, `nicvf_set_features`, `nicvf_xdp`, `nicvf_hwtstamp_get`, `nicvf_hwtstamp_set`, and `nicvf_set_rx_mode`.

## Control Flow and Integration
Probe enables PCI, requests regions, sets a 48-bit DMA mask, allocates a multi-queue netdev, maps VF CSRs, allocates per-CPU stats, initializes a queue set, registers the mailbox interrupt, sends the local `nicvf` pointer to PF, determines silicon capabilities, and registers the netdev unless this VF is a secondary queue-set-only VF. Opening the interface registers NAPI contexts, configures mailbox-mediated CPI/RSS/MTU/PTP state, requests secondary queue sets, registers data interrupts, initializes queues through `nicvf_config_data_transfer`, enables CQ/RBDR/QS interrupts, and sends `NIC_MBOX_MSG_CFG_DONE`.

RX/TX completions are consumed in `nicvf_cq_intr_handler`. RX CQEs are converted into SKBs or handled by XDP, then decorated with RX timestamp, RSS hash, queue id, checksum status, VLAN tag, and delivered through GRO or `netif_receive_skb`. TX CQEs free DMA mappings and SKBs, update BQL with `netdev_tx_completed_queue`, wake stopped TX queues, and handle PTP completion CQEs. The mailbox interrupt updates VF identity, link state, RSS size, BGX stats, PFC settings, and primary/secondary VF pointers.

## State and Persistence
Persistent runtime state is in `struct nicvf`: PF ack/nack flags, VF id, node, SQS topology, queue counts, link status, RSS table/key, PTP clock and outstanding timestamp skb, XDP program, per-CPU driver stats, hardware stats, workqueues, delayed link polling, and pointers to secondary/primary VFs. Hardware-visible state lives in VF CSRs and queue descriptors; the file itself does not persist state to disk.

## Dependencies and Risks
This file depends on `nic.h`, `nic_reg.h`, `nicvf_queues.h`, `q_struct.h`, BGX mailbox semantics, Cavium PTP support, PCI/MSI-X, NAPI, XDP, IOMMU translation, and the Linux netdev API. Risks include mailbox timeout or serialization bugs around `rx_mode_mtx`, mismatched queue accounting across primary and secondary VFs, XDP MTU/page-recycling corner cases, single-outstanding TX timestamp assumptions, recursive SQS open/stop ordering, and error paths where partial interrupt/NAPI setup must unwind cleanly.

## Test Signals
Strong signals are probe/open/stop/remove tests on PF-backed hardware or emulation, mailbox ACK/NACK/timeout coverage, multi-queue and SQS traffic, TX ring-full recovery, CQ/RBDR/QS error interrupt injection, XDP attach/detach and XDP_TX traffic, MTU rejection with XDP, hardware timestamp RX/TX validation, multicast/promiscuous mode changes, RSS indirection checks, and stats consistency against hardware counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_queues.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_queues.c

## Purpose
`nicvf_queues.c` implements ThunderX VF queue-set resource management and packet buffer movement. It allocates coherent descriptor rings, maps receive buffers, configures RQ/SQ/CQ/RBDR hardware registers and PF mailbox routing, builds send descriptors for normal, TSO, timestamped, and XDP traffic, reconstructs SKBs from receive buffer pointers, refills RBDRs, and decodes completion errors into driver stats.

## Important APIs, Types, and Functions
Queue lifecycle entry points are `nicvf_set_qset_resources`, `nicvf_config_data_transfer`, `nicvf_qset_config`, `nicvf_cmp_queue_config`, `nicvf_sq_enable`, `nicvf_sq_disable`, `nicvf_sq_free_used_descs`, and `nicvf_config_vlan_stripping`. Data-path APIs used by `nicvf_main.c` include `nicvf_sq_append_skb`, `nicvf_xdp_sq_append_pkt`, `nicvf_xdp_sq_doorbell`, `nicvf_get_rcv_skb`, `nicvf_rbdr_task`, and `nicvf_rbdr_work`. Interrupt helpers are `nicvf_enable_intr`, `nicvf_disable_intr`, `nicvf_clear_intr`, and `nicvf_is_intr_enabled`; stats/error helpers are `nicvf_update_rq_stats`, `nicvf_update_sq_stats`, `nicvf_check_cqe_rx_errs`, and `nicvf_check_cqe_tx_errs`.

## Control Flow and Integration
On enable, `nicvf_config_data_transfer` allocates RBDR, SQ, and CQ resources, then programs SQ, CQ, RBDR, and RQ hardware in that order. SQ and RQ configuration use PF mailbox messages to route queues to completion queues and buffer rings; CQ and RBDR base addresses are written directly into VF queue registers. On disable, the order reverses: RQs are disabled and synchronized through PF, RBDRs are reclaimed, SQs are stopped/reset, CQs are reset, and coherent memory plus SKB/page state is freed.

Transmit starts by calculating required subdescriptors, reserving SQ entries, writing a header subdescriptor plus gather descriptors, mapping SKB head/frags with `dma_map_page_attrs`, and ringing the SQ doorbell after a write barrier. Software TSO builds segment headers in preallocated DMA-coherent storage; hardware TSO on T88 may add dummy CQE descriptors. Receive buffer refill uses page recycling and DMA mapping to populate RBDR entries; low-memory refill switches from tasklet atomic context to delayed work in process context.

## State and Persistence
The file maintains ring state in `struct queue_set`, `struct rbdr`, `struct snd_queue`, and `struct cmp_queue`: descriptor memory, head/tail indices, free counts, page cache entries, SKB arrays, XDP page arrays, TSO header storage, interrupt thresholds, and per-queue stats. State is volatile, reconstructed on interface open, and synchronized with hardware through queue registers, doorbells, and PF mailbox commands.

## Dependencies and Risks
The code depends on exact descriptor layouts from `q_struct.h`, queue constants and types from `nicvf_queues.h`, mailbox definitions from `nic.h`, NIC register definitions, DMA/IOMMU APIs, TSO helpers, XDP APIs, and netdev queue/BQL semantics. Risk areas are DMA unmap correctness on partial mapping failures, page reference accounting for XDP recycling, queue free-count races, endian/bitfield descriptor mismatches, RBDR reclaim edge cases when FIFO is in fail state, and the use of `virt_to_phys` in software TSO payload handling.

## Test Signals
Useful signals include stress TX/RX under small rings, fragmented SKBs, software and hardware TSO, checksum offload, VLAN stripping toggles, XDP pass/drop/tx paths, memory pressure during RBDR refill, repeated open/stop cycles, DMA mapping fault injection, queue error interrupt recovery, per-queue stats validation, and lockdep/KASAN/KCSAN runs around NAPI and tasklet/delayed-work refill.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_queues.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_queues.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_queues.h

## Purpose
`nicvf_queues.h` is the public queue ABI for the ThunderX VF driver. It defines per-queue limits, default ring sizes, interrupt vector ranges, descriptor alignment requirements, queue reset/enable bits, receive/transmit error enumerations, queue state structures, descriptor access macros, and prototypes shared between `nicvf_main.c`, `nicvf_queues.c`, and related ethtool/stat paths.

## Important APIs, Types, and Constants
The header defines queue topology constants such as `MAX_RCV_QUEUES_PER_QS`, `MAX_SND_QUEUES_PER_QS`, `MAX_CMP_QUEUES_PER_QS`, interrupt ids `NICVF_INTR_ID_*`, default lengths `SND_QUEUE_LEN`, `CMP_QUEUE_LEN`, `RCV_BUF_COUNT`, thresholds for CQ/RBDR backpressure/drop, and descriptor sizes/alignment. Core structures include `q_desc_mem`, `pgcache`, `rbdr`, `rcv_queue`, `cmp_queue`, `snd_queue`, and `queue_set`. Access macros `GET_RBDR_DESC`, `GET_SQ_DESC`, and `GET_CQ_DESC` encapsulate descriptor indexing.

## Control Flow and Integration
The header does not execute control flow, but it encodes invariants assumed by the C files: one default RBDR per queue set, up to eight RQ/SQ/CQ entries per queue set, CQ/SQ interrupt vector ranges, ring lengths as power-of-two masks, receive buffer length calculation including `skb_shared_info`, and CQ/RBDR drop thresholds sized to protect transmit CQE space. Its prototypes expose queue setup, data transfer, interrupt control, RX/TX descriptor handling, and stats/error accounting to the rest of the driver.

## State and Persistence
All state described here is in-memory runtime state. Descriptor memory metadata records DMA handles and aligned base addresses. RBDR state tracks page recycling and buffer ring progress. RQ/SQ/CQ structures track enable flags, routing to completion queues, thresholds, ring pointers, SKB/XDP page backpointers, TSO header DMA storage, locks, and per-queue counters. None of this is persisted across driver reloads.

## Dependencies and Risks
The header depends on Linux netdevice, IOMMU, XDP, and `q_struct.h`. Risks are mostly contract risks: changing queue sizes or threshold values can break hardware assumptions; changing struct layout can affect cacheline behavior; `nicvf_iova_to_phys` assumes identity mapping without an IOMMU domain; and descriptor access macros rely on correct ring descriptor type and q_len masking by callers.

## Test Signals
Compile coverage across endian modes and XDP-enabled kernels is important. Runtime signals include successful queue allocation/open, RX/TX across all queues, interrupt vector naming/affinity, XDP RXQ registration, CQ error recovery, stats reads, and validation that queue length/threshold changes remain accepted by hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/nicvf_queues.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/q_struct.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/q_struct.h

## Purpose
`q_struct.h` is the hardware descriptor and queue-register layout contract for ThunderX NIC queues. It describes completion queue entries, receive buffer descriptors, send subdescriptors, RSS/CPI protocol classifications, error codes, and packed queue configuration bitfields with separate little- and big-endian definitions.

## Important APIs, Types, and Constants
Important enums include send load types, Ethernet parsing algorithms, L3/L4 type identifiers, CPI and RSS algorithms, RSS hash controls, CQE types, RX TCP status/end reasons, RX error levels/opcodes, send checksum modes, send CRC/memory operations, and SQ subdescriptor types. Major structures are `cqe_rx_t`, `cqe_rx_tcp_err_t`, `cqe_rx_tcp_t`, `cqe_send_t`, `union cq_desc_t`, `rbdr_entry_t`, `rbe_tcp_cnxt_t`, `rx_hdr_t`, `sq_crc_subdesc`, `sq_gather_subdesc`, `sq_imm_subdesc`, `sq_mem_subdesc`, `sq_hdr_subdesc`, `rq_cfg`, `cq_cfg`, `sq_cfg`, `rbdr_cfg`, and `qs_cfg`.

## Control Flow and Integration
There is no executable logic. `nicvf_queues.c` writes SQ header/gather/immediate descriptors, reads CQE RX/send fields, and casts config structs to 64-bit register values when programming RQ/CQ/SQ/RBDR/QS registers. `nicvf_main.c` interprets RX CQE fields for hash, VLAN, checksum, timestamp, queue selection, and XDP constraints. Because the definitions mirror hardware words, field order and endian guards are core integration points.

## State and Persistence
The structures represent transient DMA-visible state shared with the NIC. CQEs are written by hardware and consumed by NAPI. SQ descriptors are written by the driver and consumed by hardware. RBDR entries hold buffer DMA addresses. Queue config structs are short-lived stack objects used to produce register values. No persistent storage is involved.

## Dependencies and Risks
This header depends on architecture byteorder macros and the hardware programming manual. The largest risk is ABI drift: bitfield ordering, width, or enum value changes can corrupt DMA descriptors or registers. Another risk is that C bitfield layout is compiler- and endian-sensitive, so build coverage on supported architectures matters. Consumers also perform raw pointer arithmetic into `cqe_rx_t`, which makes word offsets sensitive to this layout.

## Test Signals
Signals include compile tests for both endian bitfield modes, hardware RX/TX smoke tests, validation of RSS/VLAN/checksum/offload fields in CQEs, TX descriptor inspection with TSO and timestamping, queue register programming tests, and regression tests for pass1 versus later silicon CQE pointer offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/q_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/thunder_bgx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/thunder_bgx.c

## Purpose
`thunder_bgx.c` is the Thunder BGX/RGX physical MAC driver. It probes BGX/RGX PCI functions, discovers LMAC modes configured by firmware, initializes SGMII/XAUI-family MAC blocks, manages link state via PHY callbacks or polling, exports services used by the NIC PF for VF-facing operations, maintains per-LMAC DMAC multicast filters, configures PFC/timestamping/loopback, and reports BGX hardware counters.

## Important APIs, Types, and Functions
Exported APIs include `bgx_get_map`, `bgx_get_lmac_count`, `bgx_get_lmac_link_state`, `bgx_get_lmac_mac`, `bgx_set_lmac_mac`, `bgx_set_dmac_cam_filter`, `bgx_set_xcast_mode`, `bgx_reset_xcast_mode`, `bgx_lmac_rx_tx_enable`, `bgx_config_timestamping`, `bgx_lmac_get_pfc`, `bgx_lmac_set_pfc`, `bgx_get_rx_stats`, `bgx_get_tx_stats`, and `bgx_lmac_internal_loopback`. Internal state is modeled with `struct bgx`, `struct lmac`, and `struct dmac_map`.

## Control Flow and Integration
Probe enables PCI resources, maps BGX registers, determines node/BGX id and maximum LMAC count, registers the BGX in the global `bgx_vnic` array, initializes RGX/XCV when applicable, reads LMAC mode/lane/training state from firmware-programmed registers, allocates dummy netdevs for PHY linkage, initializes ACPI or OF PHY/MAC data, clears global MAC filter/steering state, registers interrupts, and enables each LMAC. LMAC enable chooses SGMII/QSGMII/RGMII or XAUI/XFI/XLAUI/KR initialization, configures FCS/pad/min packet behavior, allocates DMAC filter tracking, connects PHYs when present, or starts periodic link polling.

Link changes flow through either `bgx_lmac_handler` from PHYLIB or `bgx_poll_for_link`/`bgx_poll_for_sgmii_link`. SGMII changes temporarily disable RX/TX, wait for idle, reprogram speed/duplex slot timing, then restore packet flow. XAUI-family links check SPU/SMU status and may reinitialize on receive faults. VF multicast/promiscuous requests are mediated by exported xcast/filter functions and program BGX CAM entries only after tracking per-VF references.

## State and Persistence
State is volatile and global within the module: `bgx_vnic[]`, `max_bgx_per_node`, total `lmac_count`, per-BGX register base and flags, per-LMAC MAC address, type, lane mapping, training/autoneg flags, current/last link settings, PHY pointer, workqueue, and DMAC filter reference map. Hardware registers hold MAC configuration, counters, filter CAMs, pause settings, timestamp enablement, and interrupt state.

## Dependencies and Risks
The file depends on PCI, ACPI, OF/MDIO, PHYLIB, netdevice dummy devices, `nic.h`, `nic_reg.h`, `thunder_bgx.h`, and `thunder_xcv.c` exported symbols for RGX. Risks include global indexing assumptions across nodes and BGX ids, cleanup on partial probe failures, races between VF filter changes and link/MAC reconfiguration, PHY reference lifetime in deferred probe, firmware-dependent LMAC mode discovery, and polling workqueue teardown correctness.

## Test Signals
Useful signals are probe/remove on CN81xx/CN83xx/CN88xx and RGX variants, ACPI and DT PHY discovery including `-EPROBE_DEFER`, link up/down at 10/100/1000/10000/40000 modes, PFC get/set, timestamp enable/disable, loopback, multicast filter reference sharing across VFs, BGX counter reads, TX underflow interrupt recovery, and repeated module unload during active link polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/thunder_bgx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/thunder_bgx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/thunder_bgx.h

## Purpose
`thunder_bgx.h` defines the public register, constant, type, and exported-function contract for the Thunder BGX/RGX MAC support code. It is consumed by BGX, XCV, NIC PF/VF-adjacent code, and mailbox-driven features that need link state, MAC addresses, filtering, pause, timestamping, and hardware statistics.

## Important APIs, Types, and Constants
The header defines PCI and subsystem IDs, maximum BGX/LMAC/channel/filter counts, frame and pause defaults, BGX register offsets and bit masks for CMR/SPU/SMU/GMP/MSI-X blocks, multicast mode bits, exported BGX service prototypes, XCV prototypes, BGX RX/TX stats counts, `struct bgx_stats`, and `enum LMAC_TYPE` values such as SGMII, XAUI, RXAUI, XFI, XLAUI, KR, RGMII, QSGMII, and invalid.

## Control Flow and Integration
There is no executable control flow, but the header fixes the register map used by `thunder_bgx.c` and the service API used by other Thunder NIC components. `nicvf_main.c` stores `struct bgx_stats` and reacts to BGX link/stat mailbox responses. PF-side code can call exported functions to configure BGX RX/TX, MAC filters, xcast modes, timestamping, pause, loopback, and statistics on behalf of VFs.

## State and Persistence
The file describes hardware state rather than storing it. Register macros address persistent-until-reset hardware state such as packet enable bits, filter CAM contents, link/PCS state, pause controls, timestamp insertion, interrupt enables, and counters. `struct bgx_stats` is a software snapshot buffer.

## Dependencies and Risks
The header depends on Linux integer/bool types and bit macros through includers. Risks are register ABI mismatch, incorrect LMAC mode constants, stat count drift relative to arrays and mailbox loops, and prototype changes that break symbol users. Since constants are shared across MAC and VF-facing paths, mistakes can surface as silent hardware misconfiguration rather than compile failures.

## Test Signals
Compile all Thunder NIC objects, then validate BGX probe, link mode reporting, stats loops using `BGX_RX_STATS_COUNT`/`BGX_TX_STATS_COUNT`, multicast mode changes, PFC and timestamp toggles, and RGX/XCV integration using `xcv_init_hw`/`xcv_setup_link`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/thunder_bgx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/thunder_xcv.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/thunder_xcv.c

## Purpose
`thunder_xcv.c` is the Thunder RGX/XCV companion PCI driver. It owns a small global XCV register block used by RGX LMAC support to initialize the XCV hardware and to adjust link datapath state when RGMII/RGX link status changes.

## Important APIs, Types, and Functions
The file defines XCV register offsets and bit masks, `struct xcv`, a single global `static struct xcv *xcv`, and exports `xcv_init_hw` and `xcv_setup_link`. PCI lifecycle functions are `xcv_probe`, `xcv_remove`, `xcv_init_module`, and `xcv_cleanup_module`.

## Control Flow and Integration
`xcv_probe` allocates the global XCV state, enables the PCI device, requests regions, maps the config BAR, and leaves the block ready for BGX/RGX code. `xcv_init_hw` takes DLL and clock trees out of reset, configures DLL bypass, enables the compensation controller, waits for lock, enables the port, and finally manipulates clock reset. `xcv_setup_link` maps link speed to hardware speed encoding, programs `XCV_CTL`, resets TX/RX datapaths, enables packet flow and returns credits on link up, or disables packet flow on link down. `thunder_bgx.c` calls these APIs for RGX devices.

## State and Persistence
The only software state is the global `xcv` pointer containing mapped MMIO base and PCI device. Hardware state is held in XCV reset/control/credit registers until reset or driver removal. There is no disk persistence.

## Dependencies and Risks
The file depends on PCI, MMIO accessors, sleeps during hardware bring-up, and `thunder_bgx.h` for exported prototypes. Risks include the singleton design, no locking around exported calls, `xcv_init_hw` assuming `xcv` is non-NULL when called by RGX probe, probe/remove lifetime ordering between BGX and XCV modules, and limited validation of link speeds outside 10/100/1000 defaults.

## Test Signals
Test signals include successful XCV PCI probe/remove, RGX BGX probe calling `xcv_init_hw`, link up/down transitions at 10/100/1000 Mbps, packet credit return behavior, module unload ordering, and fault injection where `pcim_iomap` or region requests fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/thunder_xcv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/Kconfig

## Purpose
This Kconfig file declares the Chelsio Ethernet driver menu and feature symbols. It gates all Chelsio Ethernet questions behind `NET_VENDOR_CHELSIO` and exposes build options for T1 (`cxgb`), optional T1 gigabit support, T3 (`cxgb3`), T4/T5/T6 PF (`cxgb4`), T4 DCB, T5 FCoE, T4/T5/T6 VF (`cxgb4vf`), the shared Chelsio library, and inline crypto subconfiguration.

## Important Symbols
`NET_VENDOR_CHELSIO` is a boolean vendor menu depending on PCI. `CHELSIO_T1` is a tristate selecting `CRC32` and `MDIO`; `CHELSIO_T1_1G` is a boolean depending on `CHELSIO_T1`. `CHELSIO_T3` depends on `PCI && INET` and selects firmware loading and MDIO. `CHELSIO_T4` depends on PCI, optional TLS compatibility, and optional PTP clock support, and selects firmware loading, MDIO, and zlib deflate. `CHELSIO_T4_DCB`, `CHELSIO_T4_FCOE`, `CHELSIO_T4VF`, and `CHELSIO_LIB` control advanced PF, VF, and library builds.

## Control Flow and Integration
Kconfig symbols flow into the Chelsio directory Makefiles. Enabling `CHELSIO_T1` includes `cxgb/` and builds the `cxgb` module; enabling later generations includes their directories. The `source "drivers/net/ethernet/chelsio/inline_crypto/Kconfig"` line nests inline crypto options under the vendor menu.

## State and Persistence
This file persists build-time configuration choices in kernel `.config`; it has no runtime state. The selected symbols determine compiled objects, modules, dependencies, and feature availability.

## Dependencies and Risks
The main dependency is PCI. Feature-specific dependencies ensure required subsystems are available. Risks include incorrect `select` usage causing missing symbols at build time, stale help URLs/docs, hidden feature coupling between T4 DCB and FCoE, and vendor menu defaults causing unexpected prompt visibility.

## Test Signals
Run `oldconfig`/`menuconfig` visibility checks and build matrix tests for built-in and module variants of T1/T3/T4/T4VF, with and without DCB/FCoE/inline crypto. Confirm that dependency-disabled symbols are not visible and that selected helper subsystems satisfy link requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/Makefile

## Purpose
This Makefile maps Chelsio Kconfig symbols to driver subdirectories. It is the top-level build dispatcher for Chelsio Ethernet support.

## Important Rules
`obj-$(CONFIG_CHELSIO_T1) += cxgb/`, `obj-$(CONFIG_CHELSIO_T3) += cxgb3/`, `obj-$(CONFIG_CHELSIO_T4) += cxgb4/`, `obj-$(CONFIG_CHELSIO_T4VF) += cxgb4vf/`, `obj-$(CONFIG_CHELSIO_LIB) += libcxgb/`, and `obj-$(CONFIG_CHELSIO_INLINE_CRYPTO) += inline_crypto/` are the complete rule set.

## Control Flow and Integration
Kbuild evaluates each `obj-*` assignment from the configured symbols. Selected directories contribute their own Makefiles and objects to either built-in kernel code or modules depending on each tristate value. This file directly integrates with `drivers/net/ethernet/chelsio/Kconfig`.

## State and Persistence
There is no runtime state. The persistent effect is in build outputs chosen by `.config`.

## Dependencies and Risks
The file depends on the subdirectories existing and their Kconfig symbols being defined. Risks are low but include symbol/name drift, missing subdirectory Makefiles, or accidentally omitting a new Chelsio component from the dispatch list.

## Test Signals
Build with each Chelsio symbol as `m` and `y`, verify that expected modules/directories are entered, and run `make W=1` for stale object or missing directory diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/Makefile

## Purpose
This Makefile defines the object composition for the Chelsio T1 `cxgb` driver. It builds `cxgb.o` when `CONFIG_CHELSIO_T1` is enabled and conditionally adds one-gigabit PHY/MAC support objects when `CONFIG_CHELSIO_T1_1G` is enabled.

## Important Rules
`obj-$(CONFIG_CHELSIO_T1) += cxgb.o` declares the module/built-in target. `cxgb-$(CONFIG_CHELSIO_T1_1G) += mv88e1xxx.o vsc7326.o` conditionally adds gigabit support. `cxgb-objs := cxgb2.o espi.o tp.o pm3393.o sge.o subr.o mv88x201x.o my3126.o $(cxgb-y)` defines the core T1 object list.

## Control Flow and Integration
Kbuild combines the listed objects into one `cxgb` driver. Core files cover adapter entry, ESPI, TP, PM3393 MAC, SGE, support routines, and 10G PHYs; optional `cxgb-y` contributes gigabit PHY/switch objects. The parent Chelsio Makefile enters this directory based on `CONFIG_CHELSIO_T1`.

## State and Persistence
The file has no runtime state. Build state is the selected object set in the generated kernel build tree.

## Dependencies and Risks
Risks include object order assumptions, optional one-gigabit symbols not being compiled when code references them, and stale object names after source moves. Because everything links into one module, missing optional guards surface as link failures.

## Test Signals
Build `CONFIG_CHELSIO_T1=m/y` with `CONFIG_CHELSIO_T1_1G=y` and `n`, inspect `cxgb.o` composition, and verify no undefined references from optional gigabit support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/common.h

## Purpose
`common.h` is the central shared header for the Chelsio T1 `cxgb` driver. It defines adapter identity, board and chip enumerations, adapter/link/port parameter structures, feature macros, common inline helpers, and prototypes for TPI access, interrupts, link negotiation, EEPROM, and software/hardware module initialization.

## Important APIs, Types, and Constants
Important constants include `DRV_DESCRIPTION`, `DRV_NAME`, `CH_DEVICE`, max port/MTU/TCB sizes, invalid link markers, PM3393/VSC7326 max frame sizes, pause/loopback capability bits, board ids, Terminator chip versions, MAC/PHY ids, pause flags, and revision ids. Key types are `adapter_t`, `struct t1_rx_mode`, `struct sge_params`, `struct chelsio_pci_params`, `struct tp_params`, `struct mc5_params`, `struct adapter_params`, `struct link_config`, `struct port_info`, `struct adapter`, and `struct board_info`.

## Control Flow and Integration
This header underpins most T1 driver objects named by `cxgb/Makefile`. `struct adapter` ties PCI/MMIO, registered/open netdev maps, params, SGE/ESPI/TP submodules, NAPI, per-port MAC/PHY/link state, work/timer state, and locks into one driver object. Inline helpers classify ASIC/chip revisions, VLAN/TSO capability, 10G capability, port iteration, board info access, and core clock conversion. Function prototypes expose cross-module operations implemented in support files.

## State and Persistence
The structures describe runtime in-memory state for each adapter and port. Hardware state is accessed through MMIO registers, TPI operations, EEPROM reads, and submodule init functions. Persistent hardware/board data can be read from serial EEPROM, but this header only declares the access path.

## Dependencies and Risks
The header depends on Linux module, netdevice, PCI, ethtool, VLAN, MDIO, CRC32, slab, I/O, and PCI id APIs. Risks include shared struct layout changes affecting many driver modules, stale capability bit definitions relative to ethtool link modes, locking contract ambiguity between `tpi_lock`, `work_lock`, `mac_lock`, and `async_lock`, and revision helpers incorrectly gating offloads.

## Test Signals
Build all cxgb objects, probe supported board ids, exercise TPI read/write paths, link negotiation, EEPROM board revision reads, module init/free paths, VLAN/TSO capability on T1B versus later chips, stats timer/work behavior, and interrupt enable/disable/slow-handler paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/cphy.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/cphy.h

## Purpose
`cphy.h` defines the PHY abstraction used by the Chelsio T1 driver. It wraps MDIO access, PHY operation callbacks, PHY instance state, convenience read/write helpers, and factory operations for supported PHY chips.

## Important APIs, Types, and Constants
`struct mdio_ops` supplies board-level MDIO init/read/write functions and mode support. PHY event/state constants cover link change, error, FIFO error, link up, autoneg ready, and autoneg enabled. `struct cphy_ops` declares lifecycle, interrupt, autoneg, advertise, loopback, speed/duplex, and link-status callbacks plus supported MMDs. `struct cphy` stores link state-machine data, adapter pointer, delayed work, BMSR/count fields, ELMER GPIO state, ops, `mdio_if_info`, and chip-specific instance data. `struct gphy` is a factory/reset interface, with extern factories for MY3126, Marvell, VSC8244, and MV88X201X.

## Control Flow and Integration
Driver code creates PHY instances through a `gphy` factory from `board_info`, initializes them with `cphy_init`, then invokes `cphy_ops` from link management and interrupt paths. `cphy_mdio_read`, `cphy_mdio_write`, `simple_mdio_read`, and `simple_mdio_write` adapt Linux MDIO callbacks to the T1 PHY abstraction. `cphy_init` binds the PHY to the netdev's adapter and populates MDIO addressing/capability fields when board MDIO ops exist.

## State and Persistence
PHY state is in-memory and per adapter port. Hardware link/autoneg state persists in the PHY registers until reset or reconfiguration, accessed through MDIO. The delayed work member supports asynchronous PHY updates, but this header only defines the container.

## Dependencies and Risks
The header depends on `common.h`, Linux MDIO definitions, netdev private data layout, and each PHY implementation honoring the callback contracts. Risks include null MDIO ops when a caller assumes them, stale `mmds`/mode support causing MDIO core misbehavior, factory/reset mismatches for multi-port PHY chips, and delayed-work lifetime issues if implementations do not cancel before freeing.

## Test Signals
Build with all supported PHY implementations, probe boards using each `gphy`, verify MDIO read/write error propagation, link status and autoneg transitions, PHY interrupt enable/clear/handler paths, loopback and speed/duplex changes, and remove/unload with pending PHY delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/cphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/cpl5_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/cpl5_cmd.h

## Purpose
`cpl5_cmd.h` defines Chelsio T1/T2 CPL5 protocol opcodes, errors, helper macros, and packed command structures. CPL messages are the firmware/hardware command and completion protocol for TCP offload, packet TX/RX, route/L2/SMT table operations, TCB manipulation, and internal MSS notifications.

## Important APIs, Types, and Constants
`enum CPL_opcode` assigns 8-bit opcode values for passive/active open, close, abort, peer close, TCB get/set, PCMD, RX/TX data, RX/TX packets, L2T/SMT/RTE operations, ARP miss, migration, errors, and `CPL_MSS_CHANGE`. `enum CPL_error` defines firmware error statuses. Helper macros `V_OPCODE`, `G_OPCODE`, `G_TID`, `MK_OPCODE_TID`, `OPCODE_TID`, and `GET_TID` pack and unpack the opcode/TID word. Major structures include open/listen/accept/establish commands, TCB commands, close/abort commands, data and packet headers, LSO headers, L2T/SMT/RTE read/write requests and replies, and `cpl_mss_change`.

## Control Flow and Integration
The header has no code flow, but driver/offload code uses these layouts to construct messages sent to the adapter and parse messages received from it. `union opcode_tid` is the common first word for connection-oriented commands. Packet TX/RX structures use endian-guarded bitfields for interface id, checksum disable/valid flags, VLAN validity, packet status, LSO header sizes, and table selectors.

## State and Persistence
The structures represent transient command/completion buffers exchanged with hardware. TIDs refer to hardware connection-table state, while L2T/SMT/RTE/TCB commands manipulate hardware tables that persist until overwritten, reset, or adapter reinitialization. The header itself stores no state.

## Dependencies and Risks
The header depends on `<asm/byteorder.h>` defining a supported bitfield endian mode and on network byte-order helpers used by consumers. Risks include opcode/value drift from firmware, unaligned command assumptions, endian bitfield mistakes, missing explicit packing if compiler layout changes, and confusion between host and network byte order in TID/opcode fields.

## Test Signals
Compile on supported endian targets, run offload command encode/decode tests, validate `GET_TID` and opcode packing, exercise TX packet and LSO descriptors, parse RX packet checksum/VLAN flags, and test L2T/SMT/RTE/TCB operations against hardware or protocol-level simulators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/cpl5_cmd.h -->
