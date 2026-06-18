# subset-b-004338 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_eth_com.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_eth_com.h

## Purpose
`ena_eth_com.h` defines the ENA Ethernet I/O communication contract used by the netdev and XDP paths. It wraps hardware descriptor preparation and completion APIs from the ENA common layer with Linux-driver-facing TX/RX context structures and fast inline helpers for doorbells, completion queue phase handling, interrupt unmasking, LLQ burst accounting, NUMA hints, and queue free-space checks.

## Important APIs, Types, And Functions
`struct ena_com_tx_ctx` carries transmit metadata: ENA metadata descriptor state, DMA buffer list, optional LLQ push header, protocol indices, checksum/TSO flags, request ID, buffer count, and header length. `struct ena_com_rx_ctx` carries received descriptor output, checksum status, hash, fragment status, descriptor count, packet offset, and buffer capacity. External APIs are `ena_com_prepare_tx()`, `ena_com_rx_pkt()`, `ena_com_add_single_rx_desc()`, and `ena_com_cq_empty()`. Inline helpers include `ena_com_free_q_entries()`, `ena_com_sq_have_enough_space()`, `ena_com_is_doorbell_needed()`, `ena_com_write_sq_doorbell()`, `ena_com_tx_comp_req_id_get()`, `ena_com_comp_ack()`, and `ena_com_cq_inc_head()`.

## Control Flow, State, And Integration
The TX path fills `ena_com_tx_ctx`, optionally checks LLQ burst capacity with `ena_com_is_doorbell_needed()`, calls `ena_com_prepare_tx()`, and rings the SQ doorbell. Completion handling reads the current CQ descriptor at `head & (q_depth - 1)`, validates the phase bit, uses `dma_rmb()` before consuming `req_id`, checks the ID against queue depth, and advances head/phase. State is transient ring state held in `ena_com_io_sq` and `ena_com_io_cq`, especially `tail`, `next_to_comp`, `head`, `phase`, cached TX metadata, LLQ entry budget, doorbell address, and interrupt registers.

## Dependencies
This header depends on `ena_com.h`, ENA descriptor definitions in `ena_eth_io_defs.h`, Linux MMIO ordering (`writel`, `dma_rmb`, `READ_ONCE`), and netdev logging. It is consumed heavily by `ena_netdev.c` and `ena_xdp.c`.

## Risks And Test Signals
The critical risks are descriptor ring wrap/phase errors, stale completion reads without the DMA barrier, LLQ free-space underestimation, invalid request IDs, and incorrect metadata caching decisions. Test signals include TX/RX traffic under ring wrap, LLQ and host-placement modes, TSO/checksum offload traffic, invalid completion fault injection, and queue stop/wake behavior under saturation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_eth_com.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_eth_io_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_eth_io_defs.h

## Purpose
`ena_eth_io_defs.h` is the generated/contract-style hardware ABI for ENA Ethernet I/O descriptors and per-CQ interrupt/NUMA registers. It defines protocol indices, TX/RX descriptor layouts, completion descriptor layouts, and bit masks/shifts used by the common ENA code to encode and decode device-visible rings.

## Important APIs, Types, And Functions
The main types are `struct ena_eth_io_tx_desc`, `struct ena_eth_io_tx_meta_desc`, `struct ena_eth_io_tx_cdesc`, `struct ena_eth_io_rx_desc`, `struct ena_eth_io_rx_cdesc_base`, `struct ena_eth_io_rx_cdesc_ext`, `struct ena_eth_io_intr_reg`, and `struct ena_eth_io_numa_node_cfg_reg`. Enums `ena_eth_io_l3_proto_index` and `ena_eth_io_l4_proto_index` define device protocol identifiers for IPv4, IPv6, TCP, UDP, RoCE, and unknown traffic. The mask/shift macros cover descriptor length, request ID split fields, phase bits, first/last/completion flags, checksum/TSO flags, header length, RX status, hash metadata, interrupt delay, and NUMA enablement.

## Control Flow, State, And Integration
There is no executable control flow. State is the packed little hardware state shared between driver memory and device DMA/MMIO. TX descriptors carry buffer addresses, offload protocol flags, and header sizing; metadata descriptors carry L3/L4 offsets and MSS for TSO; TX completion descriptors return request IDs and phase. RX descriptors publish buffers to hardware; RX completion descriptors return status, length, request ID, packet offset, hash, and checksum status. `ena_eth_com.h`, `ena_com`, `ena_netdev.c`, and `ena_xdp.c` rely on these exact fields.

## Dependencies
The file assumes kernel `BIT()` and `GENMASK()` helpers are available through including layers. It is coupled to ENA firmware/hardware ABI and to admin feature negotiation that reports max descriptors, LLQ layout, and interrupt moderation granularity.

## Risks And Test Signals
The major risk is ABI drift: a wrong bit mask, phase bit, request ID split, or length interpretation corrupts DMA rings. Test signals include descriptor packing tests in common code, RX checksum/hash validation, TSO and partial-checksum traffic, 64 KiB page-size RX buffers, interrupt moderation changes, and long stress tests that force phase-bit wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_eth_io_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_ethtool.c

## Purpose
`ena_ethtool.c` exposes ENA driver and device controls through ethtool: software/hardware statistics, link settings, interrupt coalescing, ring sizing and LLQ push-buffer length, RSS indirection/hash configuration, channel count, RX copybreak, driver info, and timestamping PHC index.

## Important APIs, Types, And Functions
Static statistic descriptors map names to offsets in `ena_stats_tx`, `ena_stats_rx`, `ena_stats_dev`, ENA admin queue stats, ENI metrics, and ENA SRD fields. `ena_get_sset_count()`, `ena_get_ethtool_stats()`, and `ena_get_ethtool_strings()` build the stats ABI. `ena_get_coalesce()`/`ena_set_coalesce()` wrap ENA interrupt moderation. `ena_get_ringparam()`/`ena_set_ringparam()` expose queue sizes and LLQ push length. RSS paths include `ena_get_rxfh()`, `ena_set_rxfh()`, `ena_get_rxfh_fields()`, `ena_set_rxfh_fields()`, and indirection table helpers. `ena_set_channels()` resizes combined queues and updates XDP feature flags. `ena_set_ethtool_ops()` installs the ops table.

## Control Flow, State, And Integration
Stats reads use `u64_stats_sync` to safely sample per-ring and adapter counters. Hardware metrics are conditional on admin capabilities: customer metrics take precedence over older ENI stats, and SRD info is appended when supported. Coalescing writes update ENA common moderation state and then per-ring cached moderation intervals. Ringparam changes are validated, rounded to powers of two, bounded by ENA minima, and handed to `ena_update_queue_params()`, which tears down and recreates queues. RSS writes update ENA common indirection/hash control tables. Channel changes call `ena_update_queue_count()` and account for XDP queue doubling requirements.

## Dependencies
This file depends on Linux ethtool/netlink APIs, PCI naming, PHC index helpers, XDP queue legality helpers, and many `ena_com_*` admin operations. It is tightly integrated with `ena_netdev.h` adapter/ring state.

## Risks And Test Signals
Risks include mismatched stat counts versus names, unsupported hardware metrics leaving holes, LLQ push-length changes requiring reset, RSS index conversion between ENA TX/RX queue numbering and combined ethtool numbering, and queue-count changes while XDP is active. Test signals include `ethtool -S`, `-c/-C`, `-g/-G`, `-l/-L`, `-x/-X`, RX hash field changes, PHC timestamp info, and XDP-on channel resize rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_netdev.c

## Purpose
`ena_netdev.c` is the core Linux PCI/netdev driver for Amazon ENA. It owns probe/remove, device initialization/reset/restore, queue allocation, MSI-X setup, NAPI polling, TX/RX data paths, watchdogs, AENQ event handlers, RSS defaults, host/debug attributes, suspend/resume, module registration, and integration with ethtool, XDP, PHC, devlink, and debugfs.

## Important APIs, Types, And Functions
The netdev ops are `ena_open()`, `ena_close()`, `ena_start_xmit()`, `ena_get_stats64()`, `ena_tx_timeout()`, `ena_change_mtu()`, `ena_xdp()`, and `ena_xdp_xmit()`. Exported helpers include `ena_xmit_common()`, `ena_unmap_tx_buff()`, `ena_init_io_rings()`, TX resource/queue range helpers, `ena_down()`, `ena_up()`, `ena_update_queue_params()`, `ena_update_queue_count()`, `ena_set_rx_copybreak()`, `ena_destroy_device()`, `ena_restore_device()`, `handle_invalid_req_id()`, `ena_unmask_interrupt()`, and `ena_update_ring_numa_node()`. Internal flows include RX allocation/refill, SKB construction, checksum/hash handling, queue creation with size backoff, MSI-X request/free, RSS initialization, watchdog timer service, and AENQ handlers.

## Control Flow, State, And Persistence
Probe enables PCI memory, maps BARs, allocates `ena_com_dev`, netdev, PHC, metrics, devlink, initializes ENA admin/device features, calculates queues and ring sizes, enables MSI-X/admin interrupts, initializes RSS, registers netdev/debugfs/devlink, and starts a timer. `ena_up()` sets IO interrupt metadata, creates NAPI, requests IRQs, creates TX/RX/XDP queues with memory backoff, refills RX, starts queues, sets DEV_UP, unmasks interrupts, and schedules NAPI. `ena_down()` clears DEV_UP, disables carrier/TX, disables NAPI, optionally resets hardware, destroys queues, frees IRQs, buffers, and resources. TX maps SKB data/frags, handles LLQ push headers, sets checksum/TSO metadata, calls `ena_xmit_common()`, manages queue stop/wake, and rings doorbells. RX polls completions, syncs DMA, optionally runs XDP, builds SKBs, handles checksums/hash, returns descriptors, refills buffers, and flushes redirects. Persistent driver state lives in `struct ena_adapter`, `ena_ring`, stats counters, flags, timers, workqueue reset task, RSS tables, host/debug buffers, and ENA admin/device state.

## Dependencies And Integration
The file depends on Linux PCI, netdevice, NAPI, DMA mapping, MSI-X, timers/workqueues, DIM, XDP, devlink, debugfs, PTP/PHC helpers, ENA admin/common APIs, and descriptor helpers. It uses AENQ link, keep-alive, and notification events to maintain link state, drop stats, and hardware hints.

## Risks And Test Signals
High-risk areas are cleanup symmetry across probe/open/reset/remove/suspend, invalid request ID handling, DMA map/unmap and RX page reuse, LLQ header copying, queue size backoff, XDP queue topology, NAPI/IRQ races, timer-triggered resets, and admin queue liveness. Test signals include probe/remove fault injection, traffic with TSO/checksum/RSS, MTU changes, ethtool ring/channel changes, XDP attach/detach/TX/redirect, suspend/resume, keep-alive timeout injection, missed TX completion detection, and memory-pressure RX refill behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_netdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_netdev.h

## Purpose
`ena_netdev.h` is the central ENA netdev state and interface header. It defines driver constants, queue index mapping, IRQ/NAPI/ring/buffer/stat structures, adapter state, flags, and cross-file prototypes shared by core netdev, ethtool, XDP, and PHC code.

## Important APIs, Types, And Functions
Important types include `struct ena_irq`, `struct ena_napi`, `struct ena_tx_buffer`, `struct ena_rx_buffer`, `struct ena_stats_tx`, `struct ena_stats_rx`, `struct ena_ring`, `struct ena_stats_dev`, and `struct ena_adapter`. Constants define module version/name, BAR indices, MSI-X vector layout, ring sizes, RX buffer limits, MTU minimums, RSS table size, queue index conversions, watchdog timeouts, and LLQ/MMIO behavior. Inline helpers include `ena_reset_device()`, `ena_increase_stat()`, and `ena_ring_tx_doorbell()`. Prototypes expose ethtool setup, stats dumping, queue parameter/count updates, RX copybreak, TX common/unmap, IO ring/resource helpers, up/down lifecycle, interrupt unmasking, NUMA updates, and invalid request ID handling.

## Control Flow, State, And Integration
This header does not implement the main control flow, but it defines the state machine used by it. `ena_adapter` stores global device state: `ena_com_dev`, netdev, PCI device, queue counts, ring sizes, MTU/offload limits, MSI-X count, PHC, flags, TX/RX rings, NAPI entries, IRQ table, reset work, timer, watchdog state, devlink, XDP program/ring range, and stats. `ena_ring` stores per-queue software resources and ENA common SQ/CQ handles. `ena_reset_device()` records a reset reason and sets the reset trigger with ordering.

## Dependencies
The header depends on Linux networking, interrupt, DIM, XDP/BPF, devlink, VLAN, and ENA common/ethernet communication headers. It is included by `ena_netdev.c`, `ena_ethtool.c`, `ena_xdp.h`, and `ena_phc.c`.

## Risks And Test Signals
Risks include cacheline-sensitive hot-path structures, hard maximums such as `ENA_PKT_MAX_BUFS`, queue index conversion mistakes, XDP rings sharing the TX ring array, and flags whose ordering controls reset behavior. Test signals are compile-time structure/API compatibility, all queue-count permutations, XDP-enabled versus disabled ring initialization, 32-bit stat synchronization, and reset reason propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_pci_id_tbl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_pci_id_tbl.h

## Purpose
`ena_pci_id_tbl.h` defines the PCI vendor/device IDs supported by the ENA driver and builds the `ena_pci_tbl[]` device table consumed by the PCI driver and module device table.

## Important APIs, Types, And Functions
The file defines `PCI_VENDOR_ID_AMAZON` when absent, ENA PF/VF and LLQ PF/VF IDs, a reserved ID, `ENA_PCI_ID_TABLE_ENTRY(devid)`, and `static const struct pci_device_id ena_pci_tbl[]`. There are no functions.

## Control Flow, State, And Integration
The table is included by `ena_netdev.c`, which passes it to `MODULE_DEVICE_TABLE(pci, ena_pci_tbl)` and to `struct pci_driver ena_pci_driver.id_table`. Kernel PCI matching uses this static data to call `ena_probe()` for matching Amazon ENA devices. There is no runtime mutable state and no persistence beyond compiled module metadata.

## Dependencies
It depends on the kernel PCI ID structures/macros being visible through including source. It is coupled to actual ENA hardware IDs and to distribution/module autoload behavior.

## Risks And Test Signals
Risks are missing or incorrect IDs causing devices not to bind, or over-broad IDs binding unsupported hardware. Test signals include `modinfo` alias output, PCI probe on PF/VF and LLQ variants, SR-IOV VF creation, and verifying reserved ID handling remains intentional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_pci_id_tbl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_phc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_phc.c

## Purpose
`ena_phc.c` integrates ENA device time with the Linux PTP Hardware Clock framework. The implementation is read-only from the host perspective: it registers a PHC when supported and enabled, provides timestamp reads with system timestamp bracketing, and rejects adjustment/set/feature operations.

## Important APIs, Types, And Functions
The PTP callbacks are `ena_phc_gettimex64()`, `ena_phc_adjtime()`, `ena_phc_adjfine()`, `ena_phc_settime64()`, and `ena_phc_feature_enable()`. Public driver APIs are `ena_phc_enable()`, `ena_phc_is_enabled()`, `ena_phc_is_active()`, `ena_phc_alloc()`, `ena_phc_free()`, `ena_phc_init()`, `ena_phc_destroy()`, and `ena_phc_get_index()`. `ena_phc_register()` and `ena_phc_unregister()` manage kernel registration.

## Control Flow, State, And Integration
Probe allocates `struct ena_phc_info`; device initialization calls `ena_phc_init()`. Initialization checks ENA PHC support and kernel/devlink enablement, initializes/configures ENA common PHC state, then registers `ptp_clock_info`. Timestamp reads lock `phc_info->lock`, bracket `ena_com_phc_get_timestamp()` with `ptp_read_system_prets()` and `ptp_read_system_postts()`, and convert nanoseconds to `timespec64`. Destroy unregisters unless a reset is in progress, preserving PHC index across reset, then destroys ENA common PHC state. On failures, PHC is disabled and the devlink PHC param is disabled.

## Dependencies
Dependencies include Linux PTP clock APIs, PCI slot naming, ENA common PHC operations, ENA adapter flags, and ENA devlink PHC parameter handling.

## Risks And Test Signals
Risks include lock ordering around timestamp reads, PHC lifetime across reset/remove, devlink enable state mismatch, and unsupported adjustment operations surprising callers. Test signals include `ethtool -T`, `/dev/ptp*` index stability across reset, timestamp reads under concurrent reset, devlink PHC toggling, and expected `-EOPNOTSUPP` for set/adjust requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_phc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_phc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_phc.h

## Purpose
`ena_phc.h` declares ENA PHC state and the PHC lifecycle/query functions shared by the core driver, ethtool timestamp reporting, devlink parameter code, and PHC implementation.

## Important APIs, Types, And Functions
`struct ena_phc_info` contains `ptp_clock_info`, registered `ptp_clock *`, back-pointer to `ena_adapter`, a spinlock, and an `enabled` flag. Public functions are `ena_phc_enable()`, `ena_phc_is_enabled()`, `ena_phc_is_active()`, `ena_phc_get_index()`, `ena_phc_init()`, `ena_phc_destroy()`, `ena_phc_alloc()`, and `ena_phc_free()`.

## Control Flow, State, And Integration
The header has no executable logic, but its state controls whether `ena_phc_init()` will register a PTP clock. `enabled` is kernel/devlink policy, while `clock` indicates active registration. `ena_ethtool.c` calls `ena_phc_get_index()` for timestamp info. `ena_netdev.c` allocates PHC state during probe, initializes during device init/restore, destroys during device teardown, and frees during remove.

## Dependencies
It depends on `<linux/ptp_clock_kernel.h>` and a visible `struct ena_adapter` declaration through including context. It is coupled to `ena_netdev.h` by the adapter’s `phc_info` pointer.

## Risks And Test Signals
Risks are mostly lifetime-related: dangling adapter pointers, double registration, freeing `phc_info` while a PTP clock is active, or incorrectly treating `enabled` as active registration. Test signals include PHC allocation/free under probe-failure unwinds, reset with PHC active, ethtool timestamp output when disabled, and devlink PHC enable/disable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_phc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_regs_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_regs_defs.h

## Purpose
`ena_regs_defs.h` defines ENA MMIO register offsets, register bit fields, and reset reason codes. It is the low-level register ABI used by ENA common code and the netdev driver when resetting or configuring the device.

## Important APIs, Types, And Functions
`enum ena_regs_reset_reason_types` enumerates reset causes including normal reset, keep-alive timeout, admin timeout, missed TX completion, invalid RX/TX request ID, too many RX descriptors, initialization error, watchdog timeout, shutdown, user trigger, missed interrupt, suspected poll starvation, and malformed RX descriptor. Macros define offsets for version, controller version, capabilities, admin queue bases/caps/doorbells, completion queue, AENQ, interrupt mask, device control/status, MMIO read request/response, RSS indirection update, and PHC doorbell. Additional masks/shifts describe version fields, capabilities, queue depths/entry sizes, device control reset reason, device status bits, MMIO read fields, RSS update fields, and PHC request ID.

## Control Flow, State, And Integration
There is no direct control flow. The reset reason enum is stored in `ena_adapter.reset_reason` and passed to `ena_com_dev_reset()`. Register offsets and masks are consumed by lower ENA common MMIO/admin code to initialize admin queues, request MMIO reads, configure RSS entries, and interact with PHC. The reset reason values are also diagnostic state visible to hardware/firmware.

## Dependencies
The file is coupled to ENA hardware/firmware register ABI and to common ENA code. It does not include Linux headers directly, so including code must provide bit macro context where needed.

## Risks And Test Signals
Risks are ABI mismatch, wrong reset reason reporting, and incorrect register mask use causing failed initialization or reset loops. Test signals include probe/reset success, MMIO readless mode, admin queue initialization, RSS indirection updates, PHC timestamp requests, and reset reason validation in device/driver logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_regs_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_xdp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_xdp.c

## Purpose
`ena_xdp.c` implements ENA XDP support beyond the inline execution helper: XDP TX frame mapping/submission, ndo XDP xmit, allocation and teardown of dedicated XDP TX queues, RX queue registration with the XDP core, XDP program attach/detach, and NAPI polling for XDP TX completions.

## Important APIs, Types, And Functions
Public APIs are `ena_xdp_xmit_frame()`, `ena_xdp_xmit()`, `ena_setup_and_create_all_xdp_queues()`, `ena_xdp_register_rxq_info()`, `ena_xdp_unregister_rxq_info()`, `ena_xdp_exchange_program_rx_in_range()`, `ena_xdp()`, and `ena_xdp_io_poll()`. Important internals are `ena_xdp_tx_map_frame()`, `ena_init_all_xdp_queues()`, `ena_destroy_and_free_all_xdp_queues()`, `ena_xdp_set()`, `validate_xdp_req_id()`, and `ena_clean_xdp_irq()`.

## Control Flow, State, And Integration
Attaching the first XDP program initializes a second set of TX rings (`xdp_first_ring = num_io_queues`, `xdp_num_queues = num_io_queues`), may bring the device down/up, exchanges program pointers on RX rings, adjusts RX headroom, and reduces `netdev->max_mtu` to `ENA_XDP_MAX_MTU`. Detach clears redirect features, tears down XDP queues, restores max MTU, and drops the old BPF program reference. XDP xmit chooses a dedicated XDP TX queue by CPU modulo queue count, serializes with `xdp_tx_lock`, maps frame data or LLQ push header into ENA TX descriptors, calls `ena_xmit_common()`, and rings the doorbell on flush. XDP NAPI cleans TX completions, validates XDP frame request IDs, unmaps DMA, returns frames, acks completions, unmasks interrupts, and updates NUMA hints.

## Dependencies
This file depends on `ena_xdp.h`, ENA netdev TX/resource helpers, Linux XDP/BPF APIs, DMA mapping via shared TX unmap code, NAPI, and queue topology from `ena_adapter`.

## Risks And Test Signals
Risks include XDP requiring twice as many queues, MTU enforcement, BPF program lifetime, RX headroom transitions, concurrent XDP_TX/XDP_REDIRECT locking, LLQ frame mapping, completion validation, and teardown while device is up. Test signals include XDP attach/detach while up/down, XDP_TX and XDP_REDIRECT traffic, ndo_xdp_xmit bulk sends, channel count changes with XDP active, max MTU changes, and completion cleanup under reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_xdp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_xdp.h

## Purpose
`ena_xdp.h` declares ENA XDP interfaces and implements the inline RX-side XDP execution helper. It defines XDP MTU constraints, XDP queue range detection, ENA-local action bits, and attach eligibility checks.

## Important APIs, Types, And Functions
Macros include `ENA_XDP_MAX_MTU`, `ENA_IS_XDP_INDEX()`, and `ENA_XDP_FORWARDED`. `enum ENA_XDP_ACTIONS` maps PASS, TX, REDIRECT, and DROP to internal bit flags. `enum ena_xdp_errors_t` reports attach eligibility. Prototypes expose queue setup, program exchange, XDP NAPI poll, frame xmit, ndo xmit, ndo BPF handler, and RX queue info registration. Inline helpers are `ena_xdp_present()`, `ena_xdp_present_ring()`, `ena_xdp_legal_queue_count()`, `ena_xdp_allowed()`, and `ena_xdp_execute()`.

## Control Flow, State, And Integration
`ena_xdp_allowed()` rejects XDP when MTU exceeds the page-backed XDP buffer budget or when normal queues cannot be doubled for dedicated XDP TX rings. `ena_xdp_execute()` reads the ring BPF program, runs it, and translates kernel XDP verdicts. `XDP_TX` converts the buffer to an `xdp_frame`, sends it through the paired XDP TX ring under `xdp_tx_lock`, and returns the frame on xmit failure. `XDP_REDIRECT` calls `xdp_do_redirect()`. Drops, aborts, invalid actions, passes, TX, and redirects update per-RX-ring stats.

## Dependencies
The header depends on `ena_netdev.h`, Linux BPF trace/XDP APIs, SKB layout constants, page size, Ethernet/VLAN constants, and shared ENA stat helpers. It is included by both the RX path in `ena_netdev.c` and the implementation in `ena_xdp.c`.

## Risks And Test Signals
Risks include only supporting single-buffer XDP in the caller, MTU/headroom/tailroom calculation errors, stale BPF program reads, failed frame conversion, redirect flush requirements, and stat correctness. Test signals include XDP_DROP/PASS/TX/REDIRECT programs, invalid action warning paths, MTU boundary tests, queue-count legality tests, and stat increments in `ethtool -S`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_xdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/7990.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/7990.c

## Purpose
`7990.c` provides generic routines for drivers built around the AMD LANCE/Am7990 Ethernet controller. Platform-specific drivers supply memory/register setup, while this file implements shared ring initialization, open/close, interrupt handling, RX/TX processing, multicast filter programming, timeout recovery, and optional netpoll.

## Important APIs, Types, And Functions
Exported APIs are `lance_open()`, `lance_close()`, `lance_tx_timeout()`, `lance_start_xmit()`, `lance_set_multicast()`, and optional `lance_poll()`. Internal helpers include register access wrappers (`WRITERAP`, `WRITERDP`, `READRDP`), `load_csrs()`, `lance_init_ring()`, `init_restart_lance()`, `lance_reset()`, `lance_rx()`, `lance_tx()`, `lance_interrupt()`, and `lance_load_multicast()`.

## Control Flow, State, And Persistence
`lance_open()` requests a shared IRQ, resets the chip, initializes the lock, and starts the queue. Reset stops CSR0, loads CSR1/2/3 with the init block address and bus-master settings, initializes TX/RX descriptors and buffers, then starts the chip after IDON. TX stops the netdev queue, copies SKB data into fixed shared-memory TX buffers, marks the descriptor owned by LANCE, advances `tx_new`, triggers transmit demand, frees the SKB, and restarts or marks the queue full based on `TX_BUFFS_AVAIL`. Interrupts ack CSR0 sources, run RX/TX completion handlers, count errors, restart after memory errors, and wake a full queue. RX copies completed frames from shared buffers into SKBs, updates stats, and returns descriptors to device ownership. Multicast changes stop TX, wait for outstanding packets, reinitialize rings, set promiscuous or multicast hash filter, reload CSRs, and restart.

## Dependencies
It depends on `7990.h`, Linux netdevice/SKB/IRQ/CRC APIs, big-endian I/O helpers, platform-specific HPLANCE/MVME register access variants, and optional HP300 LED hooks. It is built as common object code for HPLANCE and MVME147 style drivers via the AMD Makefile.

## Risks And Test Signals
Risks include legacy shared-memory assumptions, 24-bit LANCE address truncation, busy waits during multicast reconfiguration, queue stop/wake races, descriptor ownership mistakes, RX error descriptor recycling, and platform-specific register access. Test signals include open/close, TX timeout reset, interrupt RX/TX completion, multicast/promiscuous changes, carrier-loss auto-select behavior, netpoll, and error counter updates under injected CSR/descriptor errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/7990.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/7990.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/7990.h

## Purpose
`7990.h` defines the shared data structures, register offsets, descriptor flags, ring sizing defaults, address helpers, and exported function prototypes for the generic AMD LANCE/Am7990 routines in `7990.c`.

## Important APIs, Types, And Functions
Important structures are `struct lance_rx_desc`, `struct lance_tx_desc`, `struct lance_init_block`, and `struct lance_private`. Macros define LANCE register offsets (`LANCE_RDP`, `LANCE_RAP`), default TX/RX ring sizes, buffer sizes, ring masks, CSR numbers, CSR0 status/control bits, CSR3 bits, mode bits, RX/TX descriptor flags, TX error flags, `TX_BUFFS_AVAIL`, and `LANCE_ADDR()`. Prototypes expose `lance_open()`, `lance_close()`, `lance_start_xmit()`, `lance_set_multicast()`, `lance_tx_timeout()`, and optional `lance_poll()`.

## Control Flow, State, And Integration
This header has no executable control flow, but it defines the device-visible memory layout used by LANCE DMA: initialization block, RX/TX descriptor rings, and fixed packet buffers. `struct lance_private` stores CPU and LANCE-visible init block addresses, ring cursors, ring sizing, cable selection state, bus-master CSR3 value, IRQ, platform register callbacks, spinlock, and TX-full state. Platform drivers allocate/fill this state and use the exported generic routines as their netdev operations.

## Dependencies
It depends on Linux `net_device` and `sk_buff` type declarations through including source and on the legacy LANCE 24-bit bus address model. It is tightly coupled to `7990.c` and platform drivers such as HPLANCE/MVME147 users.

## Risks And Test Signals
Risks include compile-time ring-size overrides changing structure size, fixed buffer limits around Ethernet frame size, volatile descriptor access assumptions, `LANCE_ADDR()` truncation on unsuitable memory, and `TX_BUFFS_AVAIL` correctness. Test signals include structure alignment, platform allocation below LANCE addressability limits, TX/RX ring wrap, multicast filter programming, and all exported operation callbacks linked by platform drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/7990.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/Kconfig

## Purpose
`amd/Kconfig` defines the kernel configuration menu for AMD-family Ethernet drivers. It gates visibility behind `NET_VENDOR_AMD` and declares selectable drivers for legacy LANCE variants, PCI PCnet/AMD8111, AMD XGBE, and AMD/Pensando core devices.

## Important APIs, Types, And Functions
Configuration symbols include `NET_VENDOR_AMD`, `A2065`, `AMD8111_ETH`, `PCNET32`, `ARIADNE`, `ATARILANCE`, `DECLANCE`, `HPLANCE`, `MIPS_AU1X00_ENET`, `MVME147_NET`, `SUN3LANCE`, `SUNLANCE`, `AMD_XGBE`, `AMD_XGBE_DCB`, `AMD_XGBE_HAVE_ECC`, and `PDS_CORE`. Dependencies select architecture/bus prerequisites such as ZORRO, PCI, DIO, SBUS, MIPS_ALCHEMY, MVME147, SUN3, ARM64, HAS_IOMEM, and optional PTP/DCB features. Several symbols select helper libraries such as CRC32, MII, PHYLIB, BITREVERSE, AUXILIARY_BUS, and NET_DEVLINK.

## Control Flow, State, And Integration
There is no runtime control flow. Kconfig state controls which objects in the AMD Makefile are built and what dependencies become available. The `NET_VENDOR_AMD` menu prevents irrelevant prompts on unsupported platforms. The common `7990.o` code is pulled indirectly by Makefile entries for HPLANCE and MVME147 when their config symbols are enabled.

## Dependencies
This file depends on Linux Kconfig semantics and architecture symbols. It integrates with `drivers/net/ethernet/amd/Makefile` and documentation references for PDS core.

## Risks And Test Signals
Risks include missing dependencies causing build failures on uncommon architectures, over-restrictive dependencies hiding valid drivers, missing selected libraries, and stale help text/module names. Test signals include `allyesconfig`, `allmodconfig`, architecture-specific configs for m68k/Sparc/MIPS/PCI, and verifying selected modules match Makefile object names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/Makefile

## Purpose
`amd/Makefile` maps AMD Ethernet Kconfig symbols to build objects and subdirectories. It is the build glue for legacy AMD LANCE drivers, PCI drivers, AMD XGBE, and AMD/Pensando core support.

## Important APIs, Types, And Functions
The important entries are `obj-$(CONFIG_A2065) += a2065.o`, `obj-$(CONFIG_AMD8111_ETH) += amd8111e.o`, `obj-$(CONFIG_ARIADNE) += ariadne.o`, `obj-$(CONFIG_ATARILANCE) += atarilance.o`, `obj-$(CONFIG_DECLANCE) += declance.o`, `obj-$(CONFIG_HPLANCE) += hplance.o 7990.o`, `obj-$(CONFIG_MIPS_AU1X00_ENET) += au1000_eth.o`, `obj-$(CONFIG_MVME147_NET) += mvme147.o 7990.o`, `obj-$(CONFIG_PCNET32) += pcnet32.o`, `obj-$(CONFIG_SUN3LANCE) += sun3lance.o`, `obj-$(CONFIG_SUNLANCE) += sunlance.o`, `obj-$(CONFIG_AMD_XGBE) += xgbe/`, and `obj-$(CONFIG_PDS_CORE) += pds_core/`.

## Control Flow, State, And Integration
There is no runtime flow. Kbuild evaluates enabled config symbols and compiles or descends into the listed objects/directories. The key integration point for this work item is that `7990.o` is shared by both HPLANCE and MVME147, so changes to generic LANCE routines affect both platform drivers.

## Dependencies
It depends on symbols declared in `amd/Kconfig`, Kbuild object syntax, and the source files/subdirectories being present. Build ordering is simple object aggregation.

## Risks And Test Signals
Risks include duplicate inclusion of common objects if multiple configs are built into the same linkage unit, stale object names, and missing subdirectory wiring. Test signals include building combinations of `CONFIG_HPLANCE` and `CONFIG_MVME147_NET`, AMD allmodconfig coverage, and verifying modules contain expected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/Makefile -->
