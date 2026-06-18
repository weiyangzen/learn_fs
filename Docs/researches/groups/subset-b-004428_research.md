# Research Group: subset-b-004428

This grouped report covers the requested Google GVE DQO TX helper subset and Hisilicon Ethernet driver subset. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_tx_dqo.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_tx_dqo.c

## Purpose

This file implements the DQO transmit datapath for the Google Virtual Ethernet driver. It allocates and tears down DQO TX rings, posts SKB, XDP, and AF_XDP descriptors, manages optional queue-page-list copy buffers, handles descriptor and packet completions, tracks miss/reinjection completions, and integrates TX cleaning with NAPI notification blocks.

## Important APIs, Types, and Functions

- `gve_tx_alloc_rings_dqo()`, `gve_tx_free_rings_dqo()`, `gve_tx_start_ring_dqo()`, and `gve_tx_stop_ring_dqo()` are the lifecycle entry points used by the broader GVE device setup/teardown code.
- `gve_tx_dqo()` is the `ndo_start_xmit`-style SKB transmit entry for DQO rings. It calls `gve_try_tx_skb()`, batches doorbells with `netdev_xmit_more()`, and returns `NETDEV_TX_BUSY` when resource throttling is required.
- `gve_xdp_xmit_dqo()`, `gve_xdp_xmit_one_dqo()`, `gve_xdp_poll_dqo()`, `gve_xdp_tx_flush_dqo()`, and `gve_xsk_tx_poll_dqo()` cover XDP redirect/transmit and AF_XDP TX.
- `gve_clean_tx_done_dqo()` consumes completion descriptors and updates BQL, per-ring statistics, completion tags, and pending-packet state.
- `struct gve_tx_pending_packet_dqo` instances are the completion-tag state objects for SKBs, XDP frames, and XSK descriptors. They carry DMA unmap metadata, SKB/XDP frame pointers, QPL buffer IDs, state, linked-list pointers, and timeout jiffies.
- `gve_tx_fill_pkt_desc_dqo()`, `gve_tx_fill_tso_ctx_desc()`, and `gve_tx_fill_general_ctx_desc()` materialize hardware descriptors in the DQO TX ring.
- `gve_prep_tso()`, `gve_can_send_tso()`, and `gve_features_check_dqo()` enforce hardware descriptor limits for TSO/GSO.

## Control Flow

Ring allocation computes a safe pending-packet count from the completion-queue size, subtracting room for descriptor completions and possible miss/reinjection completions. Each ring gets a pending-packet array, optional XSK reorder queue, DMA-coherent TX and completion rings, queue resources, and, in QPL mode, a queue page list plus a freelist of fixed-size TX copy buffers.

Transmit first estimates data descriptor and buffer requirements. In raw-addressing mode it counts the SKB head and frags after splitting at `GVE_TX_MAX_BUF_SIZE_DQO`; in QPL mode it counts 2 KiB copy buffers. `gve_maybe_stop_tx_dqo()` checks pending-packet objects, ring slots, and QPL buffers, stops the netdev queue on shortage, uses a memory barrier to synchronize with the cleaner, and immediately rechecks to avoid a stop/wake race.

For SKBs, `gve_tx_add_skb_dqo()` allocates a completion tag, records the SKB, emits an optional TSO context descriptor, always emits a general context descriptor, then either maps SKB storage directly or copies packet bytes into QPL buffers. It advances the tail and occasionally requests descriptor report events. `gve_tx_dqo()` rings the doorbell immediately unless xmit-more batching says more packets are coming.

Completion polling walks the completion ring until the generation bit says hardware still owns the descriptor or the NAPI packet budget is reached. Descriptor completions update the cached hardware head. Packet completions free QPL buffers or DMA mappings and release SKBs/XDP frames. Miss completions move packets to a miss list and account BQL completion before waiting for reinjection. Reinjection completions complete those missed packets. Timeout processing drops packets that never receive reinjection and later frees the tag after a deallocation grace period.

AF_XDP TX peeks descriptors from the XSK pool, fills packet descriptors directly against pool DMA addresses, pushes completion tags into a reorder queue, and only reports completions to the XSK pool in original order after packet state becomes `GVE_PACKET_STATE_XSK_COMPLETE`.

## State and Persistence

State is entirely runtime kernel/device state. Ring state includes software head/tail pointers, atomic completion-side freelists for pending packets and QPL buffers, posted/completed descriptor counters, completion generation bit, miss and timed-out linked lists, XSK reorder head/tail, and u64 stats. QPL buffer ownership persists across TX and completion contexts using atomic head/count handoff. DMA mappings persist from descriptor posting until packet completion, timeout cleanup, or ring stop. Hardware state persists in coherent descriptor rings and queue doorbells until the ring is reset or freed.

## Dependencies and Integration Points

The file depends on GVE core structures from `gve.h`, admin queue/page-list helpers, DQO descriptor definitions, the Linux DMA API, BQL, NAPI, XDP, AF_XDP, SKB GSO/checksum helpers, and netdev TX queue APIs. It integrates with notify blocks through `gve_utils.c`, with queue allocation/configuration through GVE adminq code, and with RX-side XSK polling through the XDP TX queue mapping helpers.

## Risks and Edge Cases

The code is resource-accounting heavy. Bugs in pending-packet freelists, QPL buffer counts, or descriptor-count estimation can stop queues permanently or overrun rings. The miss/reinjection model intentionally treats several completion orderings as invalid; those paths are rate-limited errors and can leave packets waiting for timeout. QPL and raw-addressing cleanup differ, so error paths must match allocation mode exactly. `gve_maybe_stop_tx_dqo()` contains two `netif_tx_start_queue()` calls in the recovery branch, which is harmless but suspicious. XSK completion reporting depends on reorder-queue ordering rather than hardware order. TSO eligibility is constrained by per-segment descriptor count; incorrect checks would surface as device-side drops or disabled GSO.

## Test Signals

Useful signals include successful DQO ring allocation/free for raw-addressing and QPL modes, SKB TX under BQL pressure with queue stop/wake, TSO and non-TSO packets with many frags, DMA mapping failure injection, XDP redirect and AF_XDP TX completion ordering, miss/reinjection completion handling, reinjection timeout drops, clean `gve_tx_stop_ring_dqo()` without leaked SKBs or DMA mappings, and counters such as `pkt_done`, `bytes_done`, `dropped_pkt`, `xdp_xmit_errors`, and `xdp_xsk_sent`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_tx_dqo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_utils.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_utils.c

## Purpose

This file provides small shared helpers for GVE queue/notification block wiring, RX copy fallback, page reference bias maintenance, and NAPI add/remove handling.

## Important APIs, Types, and Functions

- `gve_tx_was_added_to_block()`, `gve_tx_add_to_block()`, and `gve_tx_remove_from_block()` manage the TX pointer stored in `struct gve_notify_block`.
- `gve_rx_was_added_to_block()`, `gve_rx_add_to_block()`, and `gve_rx_remove_from_block()` do the same for RX rings.
- `gve_rx_copy_data()` and `gve_rx_copy()` allocate a NAPI SKB and copy packet bytes from a linear pointer or a `struct gve_rx_slot_page_info`.
- `gve_dec_pagecnt_bias()` maintains the high page reference bias used by page-reuse RX paths.
- `gve_add_napi()` and `gve_remove_napi()` attach/detach a notify block's NAPI instance and IRQ.

## Control Flow

TX and RX add helpers derive the notify-block index from queue index, store the ring pointer into the notify block, and record the notify ID on the ring. TX add also sets XPS for the queue using the notify index modulo active CPUs. NAPI add registers the poll function with `netif_napi_add_locked()`, associates the IRQ, and enables the IRQ. NAPI remove disables the IRQ before deleting the NAPI instance.

## State and Persistence

The file mutates pointers in `priv->ntfy_blocks[]`, ring `ntfy_id` fields, XPS CPU masks, RX page reference bias counters, and NAPI/IRQ registration state. There is no file-local persistent state.

## Dependencies and Integration Points

The helpers are shared by GVE RX/TX implementations, including DQO and non-DQO paths. They depend on `gve_tx_idx_to_ntfy()`, `gve_rx_idx_to_ntfy()`, netdev XPS, NAPI, IRQ APIs, SKB allocation, and the RX page-info layout from GVE core headers.

## Risks and Edge Cases

The add/remove helpers assume callers serialize lifecycle transitions. Removing NAPI while interrupts or poll callbacks are still active would be unsafe. `gve_tx_add_to_block()` divides by `active_cpus`, computed as `min(priv->num_ntfy_blks / 2, num_online_cpus())`; invalid notification-block sizing could make that zero. RX copy allocation can fail and returns `NULL`. Page bias reset relies on a current `page_count()` snapshot and must not race with unexpected page ownership changes.

## Test Signals

Signals include correct notify-block TX/RX pointers during queue start/stop, NAPI IRQ association and disable on teardown, XPS masks matching notify block distribution, RX copy fallback producing valid Ethernet SKBs, and page reuse under stress without refcount underflow or leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_utils.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_utils.h

## Purpose

This header declares shared GVE helper functions implemented in `gve_utils.c` for queue notification block management, RX packet copying, page bias accounting, and NAPI lifecycle.

## Important APIs, Types, and Functions

The exported declarations cover TX/RX add/remove/status helpers, `gve_rx_copy_data()`, `gve_rx_copy()`, `gve_dec_pagecnt_bias()`, `gve_add_napi()`, and `gve_remove_napi()`. It includes `gve.h` and `<linux/etherdevice.h>` so callers see the GVE private structures and netdev types.

## Control Flow

There is no runtime control flow in this header. It establishes compile-time function contracts for GVE source files.

## State and Persistence

No state is stored here. State effects happen in the implementation and callers.

## Dependencies and Integration Points

The header integrates multiple GVE RX/TX implementations with common helpers and must remain consistent with the function definitions in `gve_utils.c`.

## Risks and Edge Cases

Prototype drift would break builds or, if types changed incompatibly in related headers, cause incorrect caller assumptions about object ownership and NAPI locking context. The header is small but central to TX/RX lifecycle code.

## Test Signals

Build coverage of all GVE objects using this header is the primary signal. Runtime signals are the same queue/NAPI/RX-copy behavior covered by `gve_utils.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/Kconfig

## Purpose

This Kconfig file exposes Hisilicon Ethernet driver build options, including older ARM/ARM64 platform MACs, HNS/HNS3 framework drivers, and the PCI-based HIBMCGE BMC Gigabit Ethernet driver.

## Important APIs, Types, and Functions

- `NET_VENDOR_HISILICON` gates the vendor menu and depends on `OF || ACPI`.
- `HIX5HD2_GMAC`, `HISI_FEMAC`, and `HIP04_ETH` enable platform MAC drivers and select required PHY, reset, MFD, and MDIO support.
- `HI13X1_GMAC` is a bool variant depending on `HIP04_ETH`.
- `HNS`, `HNS_MDIO`, `HNS_DSAF`, and `HNS_ENET` configure the HNS framework and first-generation acceleration/enet drivers.
- `HNS3`, `HNS3_HCLGE`, `HNS3_DCB`, `HNS3_HCLGEVF`, and `HNS3_ENET` configure the PCI HNS3 stack.
- `HIBMCGE` enables the BMC GE PCI driver and selects `PHYLIB`, `FIXED_PHY`, Motorcomm/Realtek PHY drivers, and `PAGE_POOL`.

## Control Flow

There is no runtime control flow. Kconfig dependency resolution controls which objects Kbuild compiles and whether related subsystems are selected.

## State and Persistence

State is kernel configuration state in `.config`. Those choices persist into build artifacts and module availability.

## Dependencies and Integration Points

The file integrates Hisilicon Ethernet drivers with PHYLIB, reset controller support, MFD/syscon, HNS MDIO, HNAE/HNS/HNS3 frameworks, PCI/MSI, devlink, DIMLIB, PTP optional support, fixed PHY, and page pool.

## Risks and Edge Cases

Incorrect dependencies can produce unresolved symbols, especially around PCI/MSI, PHY drivers, reset APIs, or page-pool use. Several platform drivers are guarded by `ARM || ARM64 || COMPILE_TEST`, while `HIBMCGE` is outside that block and depends on PCI/MSI only. The `HIP04_ETH` help text and `HNS_DSAF` help contain typos, but they do not affect builds.

## Test Signals

Build matrix signals include `allmodconfig`, `COMPILE_TEST`, `HIBMCGE=m/y`, legacy platform drivers as modules, HNS/HNS3 combinations, and disabled `NET_VENDOR_HISILICON`. Link success and expected module objects are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/Makefile

## Purpose

This Makefile maps Hisilicon Ethernet Kconfig symbols to the driver objects and subdirectories built by Kbuild.

## Important APIs, Types, and Functions

It builds `hix5hd2_gmac.o`, `hip04_eth.o`, `hns_mdio.o`, `hisi_femac.o`, the `hns/` and `hns3/` subdirectories, and the `hibmcge/` subdirectory according to their `CONFIG_*` symbols.

## Control Flow

There is no runtime control flow. Kbuild includes objects and subdirectories based on configuration.

## State and Persistence

The file affects build artifacts only.

## Dependencies and Integration Points

It integrates with the local Kconfig symbols and delegates composite driver construction to subdirectory Makefiles for HNS, HNS3, and HIBMCGE.

## Risks and Edge Cases

Object names must match source files and Kconfig symbols exactly. Missing subdirectory inclusion would silently omit configured drivers. Tristate combinations should be verified for module and built-in builds.

## Test Signals

Expected outputs include direct objects for selected platform MACs and recursive builds for `hns/`, `hns3/`, and `hibmcge/` when their symbols are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/Makefile

## Purpose

This Makefile builds the HIBMCGE driver as a composite object from its lifecycle, hardware, MDIO, IRQ, TX/RX, ethtool, debugfs, error recovery, and diagnostics source files.

## Important APIs, Types, and Functions

- `ccflags-y += -I$(src)` ensures local headers are available.
- `obj-$(CONFIG_HIBMCGE) += hibmcge.o` selects the composite object.
- `hibmcge-objs` lists `hbg_main.o`, `hbg_hw.o`, `hbg_mdio.o`, `hbg_irq.o`, `hbg_txrx.o`, `hbg_ethtool.o`, `hbg_debugfs.o`, `hbg_err.o`, and `hbg_diagnose.o`.

## Control Flow

No runtime control flow exists. Kbuild links the listed objects into one module or built-in object.

## State and Persistence

Only build state is affected.

## Dependencies and Integration Points

The composite arrangement allows `hbg_main.c` to register the PCI driver while the other files provide helper symbols in the same final object.

## Risks and Edge Cases

The object list must include every file that defines non-static symbols used by the driver. Missing `hbg_trace.h` is expected because it is included by `hbg_txrx.c` for tracepoint generation rather than compiled directly.

## Test Signals

Build `CONFIG_HIBMCGE=m` and verify `hibmcge.ko` contains the module metadata from `hbg_main.c` and resolves helper symbols from all listed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_common.h

## Purpose

This header defines the shared data model, constants, enums, and cross-file scheduling declarations for the HIBMCGE driver.

## Important APIs, Types, and Functions

- Constants define status values, RX skip/header layout, vector count, packet header size, TX timeout log size, and `HBG_NO_PHY`.
- `enum hbg_dir`, `enum hbg_tx_state`, `enum hbg_nic_state`, `enum hbg_reset_type`, and `enum hbg_hw_event_type` describe ring direction, TX descriptor state, driver state bits, reset source, and firmware/hardware event types.
- `struct hbg_buffer` holds SKB/page DMA state, TX completion state DMA address, direction, and back-pointers.
- `struct hbg_ring` represents TX or RX software rings, including coherent buffer array, head/tail aliases, NAPI object, page pool, and timeout log buffer.
- `struct hbg_dev_specs` caches device-provided capabilities such as MAC ID, PHY address, FIFO sizes, MTU range, VLAN layers, MAC table size, frame size, and RX buffer size.
- `struct hbg_irq_info` and `struct hbg_vector` describe IRQ metadata and per-IRQ counters.
- `struct hbg_mac`, `struct hbg_mac_filter`, `struct hbg_user_def`, `struct hbg_stats`, and `struct hbg_priv` are the core per-device state containers.
- `hbg_err_reset_task_schedule()` and `hbg_np_link_fail_task_schedule()` are declared for async service-task triggers.

## Control Flow

The header itself has no control flow. It enables all HIBMCGE modules to share one `struct hbg_priv` and common enums for lifecycle, reset, IRQ, ring, stats, and PHY operations.

## State and Persistence

All persistent runtime driver state is represented here: PCI/netdev pointers, BAR base, device specs, state bits, PHY/MDIO handles, vector stats, TX/RX rings, MAC filter table, saved user pause settings, accumulated stats, last stats-update time, and delayed service work.

## Dependencies and Integration Points

The header depends on ethtool, netdevice, PCI, page pool helpers, and `hbg_reg.h`. It is included by nearly every HIBMCGE source file and forms the integration contract among hardware helpers, TX/RX, ethtool, debugfs, MDIO, IRQ, diagnostics, and reset recovery.

## Risks and Edge Cases

Because this is a shared state header, layout changes can affect stats offset macros, DMA state handling, debugfs output, diagnostics, and reset restoration. `struct hbg_stats` is consumed via offset arithmetic in ethtool and diagnose paths, so field additions need synchronized table updates. The comment "rest" in the user settings comment is a typo only.

## Test Signals

Compile all HIBMCGE objects after any structure changes, verify ethtool stats offsets, debugfs state display, diagnostics pushes, reset restore behavior, and TX/RX ring initialization using the shared fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_debugfs.c

## Purpose

This file exposes debugfs diagnostics for HIBMCGE ring occupancy, IRQ metadata, MAC filter entries, and reset/link state.

## Important APIs, Types, and Functions

- `hbg_debugfs_register()` creates the global `hibmcge` debugfs root.
- `hbg_debugfs_init()` creates one per-PCI-device directory and devm seqfiles for `tx_ring`, `rx_ring`, `irq_info`, `mac_table`, and `nic_state`.
- `hbg_debugfs_unregister()` removes the global root at module exit.
- `hbg_dbg_ring()`, `hbg_dbg_irq_info()`, `hbg_dbg_mac_table()`, and `hbg_dbg_nic_state()` are the seqfile renderers.

## Control Flow

Module init creates the global root before PCI driver registration. Device init creates a child directory named by `pci_name()` and registers devm seqfiles. Each file reads live driver state and hardware registers when opened. Device cleanup removes the per-device subtree through a devm action; module exit removes the global root.

## State and Persistence

The only file-local state is `hbg_dbgfs_root`. Per-device debugfs files reflect live state from `struct hbg_priv`, including ring indices, FIFO occupancy, IRQ enabled bits/counters, MAC table contents, reset flags, and NP link status.

## Dependencies and Integration Points

The file depends on debugfs, seq_file, PCI device names, string-choice helpers, hardware IRQ/FIFO helpers, and TX/RX queue helpers. It integrates with `hbg_main.c` module/device lifecycle and shared state from `hbg_common.h`.

## Risks and Edge Cases

Debugfs failures are intentionally ignored because debugfs is not a functional requirement. Renderers read live state without heavy locking, so values are snapshots and may race with TX/RX or reset. `reset_type_str[priv->reset_type]` assumes reset type stays within enum range.

## Test Signals

Signals include `/sys/kernel/debug/hibmcge/<pci>/` creation, readable `tx_ring`, `rx_ring`, `irq_info`, `mac_table`, and `nic_state` files, removal after device unbind/module unload, and no crashes while reading during traffic or reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_debugfs.h

## Purpose

This header declares the HIBMCGE debugfs lifecycle functions.

## Important APIs, Types, and Functions

It declares `hbg_debugfs_register()`, `hbg_debugfs_unregister()`, and `hbg_debugfs_init()`.

## Control Flow

There is no runtime control flow in the header. `hbg_main.c` calls these functions during module and device initialization/exit.

## State and Persistence

No state is defined here.

## Dependencies and Integration Points

The declarations integrate `hbg_debugfs.c` with the main driver lifecycle.

## Risks and Edge Cases

Prototype drift would break module initialization or leave debugfs resources unmanaged.

## Test Signals

Build coverage and debugfs creation/removal tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_diagnose.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_diagnose.c

## Purpose

This file implements a driver-to-BMC diagnostic push channel. When firmware requests data, the driver pushes IRQ counters, link status, and selected software/hardware statistics through message registers.

## Important APIs, Types, and Functions

- `struct hbg_diagnose_message` is the temporary message container with opcode, status, data count, device pointer, and up to 64 `u32` data words.
- `hbg_push_irq_list` and `hbg_push_stats_list` map stable numeric IDs to IRQ masks and `struct hbg_stats` offsets.
- `hbg_push_msg_send()` writes message data registers, formats the header, starts the push, and polls until hardware clears the status bit.
- `hbg_push_data()` and `hbg_push_data_u64()` chunk arbitrary `u32`/`u64` arrays into the 64-word payload limit.
- `hbg_diagnose_message_push()` is the public service-task entry point.

## Control Flow

The service task calls `hbg_diagnose_message_push()`. It exits during reset or unless `HBG_REG_PUSH_REQ_ADDR` equals 1. It then pushes IRQ counts, link status, and stats in order. Any failure logs an error and skips to completion. Completion always clears the push request register.

## State and Persistence

The file reads persistent counters from `priv->vectors.stats_array` and `priv->stats`; it does not own long-lived state. Message payload buffers are allocated transiently with `kcalloc()`. Hardware message registers hold the in-flight payload and response code.

## Dependencies and Integration Points

It depends on hardware register access helpers, `hbg_ethtool.h` stats-offset macros, PHY link state, IRQ metadata, and the periodic service task in `hbg_main.c`.

## Risks and Edge Cases

`hbg_push_msg_send()` ignores the return value of `readl_poll_timeout()` and derives the return from the response-code field, so a timeout is only visible if the register retains the initialized response code. `hbg_push_link_status()` dereferences `priv->mac.phydev`, so diagnostics require successful PHY/fixed-PHY init. Stats list IDs must stay synchronized with the BMC consumer. The u64-to-u32 cast assumes endianness and word order agreed with firmware/BMC.

## Test Signals

Signals include BMC-triggered push request clearing, successful IRQ/link/stats messages, timeout/error logging on unresponsive hardware, correct ID/value pairs in the BMC receiver, and no pushes while reset is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_diagnose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_diagnose.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_diagnose.h

## Purpose

This header declares the HIBMCGE diagnostic push entry point.

## Important APIs, Types, and Functions

It includes `hbg_common.h` and declares `hbg_diagnose_message_push(struct hbg_priv *priv)`.

## Control Flow

No control flow is present in the header. The service task calls the declared function.

## State and Persistence

No state is stored here.

## Dependencies and Integration Points

It connects `hbg_main.c` service work to `hbg_diagnose.c`.

## Risks and Edge Cases

Prototype drift would break the periodic diagnostics integration.

## Test Signals

Build coverage and BMC diagnostic push behavior validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_diagnose.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_err.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_err.c

## Purpose

This file implements HIBMCGE reset/rebuild logic and PCI error-recovery callbacks.

## Important APIs, Types, and Functions

- `hbg_rebuild()` reruns hardware initialization and restores user-visible settings.
- `hbg_reset()` performs a function reset when the netdev is down.
- `hbg_err_reset()` closes the netdev if running, resets/rebuilds under RTNL, and reopens it.
- `hbg_set_pci_err_handler()` installs the driver's `struct pci_error_handlers`.
- PCI callbacks handle `error_detected`, `slot_reset`, `reset_prepare`, and `reset_done`.

## Control Flow

Reset preparation serializes with `HBG_NIC_STATE_RESETTING`, rejects resets while the port is up for direct `hbg_reset()` calls, detaches the netdev, records reset type, clears failure state, and asks hardware/firmware for `HBG_HW_EVENT_RESET`. Reset completion checks the reset type, rebuilds hardware state, reattaches the netdev, and clears the resetting bit. Error-triggered reset closes the interface first, so reset preparation sees a down port.

PCI AER handling reports permanent failure as disconnect, otherwise requests reset. Slot reset reenables PCI, restores state, and invokes `hbg_err_reset()`. FLR prepare/done callbacks use the same reset-prepare/done helpers with `HBG_RESET_TYPE_FLR`.

## State and Persistence

Reset preserves and restores MAC table entries, MTU, pause settings, RX pause MAC address, filter enablement, and accumulated stats. It mutates `priv->state`, `priv->reset_type`, and `reset_fail_cnt`.

## Dependencies and Integration Points

The file depends on RTNL, PCI error recovery, PHY/netdev close/open behavior, hardware event notifications, hardware init, MAC filter state, and ethtool pause settings. It is called from IRQ error handling, service task, ethtool reset, and PCI AER.

## Risks and Edge Cases

Direct `hbg_reset()` refuses to run while the netdev is up, so callers must close first or use `hbg_err_reset()`. Failed hardware reset leaves reset-fail state and may keep the device detached. Restore assumes the saved MAC filter table and pause settings are valid. PCI slot reset calls `pci_disable_device()` before reenable; state restoration must match what pcim/device-managed setup expects.

## Test Signals

Signals include ethtool dedicated reset while down, IRQ-triggered reset while up, PCI AER reset callbacks, restoration of MAC address/filter/pause/MTU, reset failure counter increments on hardware timeout, and clean netdev detach/attach transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_err.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_err.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_err.h

## Purpose

This header declares HIBMCGE reset/rebuild and PCI error-handler integration functions.

## Important APIs, Types, and Functions

It declares `hbg_set_pci_err_handler()`, `hbg_reset()`, `hbg_rebuild()`, and `hbg_err_reset()`.

## Control Flow

The header has no runtime control flow. Callers use the declarations from main lifecycle, ethtool, IRQ/service recovery, and PCI setup.

## State and Persistence

No state is declared here.

## Dependencies and Integration Points

It includes PCI declarations and links error recovery implementation into other HIBMCGE modules.

## Risks and Edge Cases

Prototype mismatch would break reset or AER integration at build time.

## Test Signals

Build coverage and reset/AER behavior validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_ethtool.c

## Purpose

This file provides HIBMCGE ethtool operations: register dump, pause configuration, dedicated reset, standard PHY link settings, string/stat reporting, pause/MAC/control/RMON statistics, and periodic hardware-stat accumulation.

## Important APIs, Types, and Functions

- `struct hbg_ethtool_stats` maps ethtool stat names to `struct hbg_stats` offsets and optional hardware registers.
- `hbg_update_stats()` accumulates all register-backed stats into `priv->stats`.
- `hbg_ethtool_get_regs_len()` and `hbg_ethtool_get_regs()` implement `ethtool -d` register dumps using `struct hbg_reg_info`.
- Pause operations read/write hardware pause enable bits and synchronize PHY asym-pause settings.
- `hbg_ethtool_reset()` accepts only `ETH_RESET_DEDICATED` and delegates to `hbg_reset()`.
- `hbg_ethtool_set_ops()` installs the static `ethtool_ops`.

## Control Flow

Etntool stat reads call `hbg_update_stats()` first, then copy selected fields out of `priv->stats`. Register dumps copy the static register descriptor, read the absolute register, then adjust the offset to be relative to its dump type. Pause set updates the driver's saved autoneg and pause settings, programs PHY advertisement, and writes hardware bits immediately when autoneg is disabled.

## State and Persistence

The driver accumulates 32-bit hardware counters into 64-bit `priv->stats`. User pause settings persist in `priv->user_def.pause_param` for reset restoration. Register dump state is transient. `hbg_update_stats_by_info()` skips updates during reset.

## Dependencies and Integration Points

The file depends on PHY ethtool helpers, RTNL-visible netdev operations, register definitions, hardware pause helpers, stats offset macros from `hbg_ethtool.h`, reset helpers, and the service task that periodically calls `hbg_update_stats()` to avoid 32-bit register overflow.

## Risks and Edge Cases

Register-backed stats are added every update, so this assumes hardware registers are clear-on-read or delta-like; if registers are absolute counters, repeated reads would overcount. The generic stats string set exposes only `hbg_ethtool_stats_info`, while MAC/control/RMON stats are available through structured ethtool callbacks. Reset through ethtool fails if the interface is up because `hbg_reset()` rejects up ports. Stats reads are mostly unlocked snapshots.

## Test Signals

Signals include `ethtool -S`, `ethtool -d`, pause get/set with autoneg on/off, `ethtool --reset dedicated` while down, structured MAC/control/RMON stats, periodic accumulation over more than 30 seconds, and no stat updates during reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_ethtool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_ethtool.h

## Purpose

This header defines HIBMCGE stats offset helpers and declares ethtool/stat functions.

## Important APIs, Types, and Functions

- `HBG_STATS_FIELD_OFF(f)` computes a field offset within `struct hbg_stats`.
- `HBG_STATS_R(p, offset)` reads a u64 stat through offset arithmetic.
- `HBG_STATS_U(p, offset, val)` adds a value to a u64 stat.
- It declares `hbg_ethtool_set_ops()` and `hbg_update_stats()`.

## Control Flow

No control flow is present. The macros are expanded by ethtool and diagnostics code.

## State and Persistence

No state is declared, but the macros operate on persistent `struct hbg_stats` storage.

## Dependencies and Integration Points

The header integrates stats tables in `hbg_ethtool.c` and `hbg_diagnose.c` with the shared stats layout in `hbg_common.h`.

## Risks and Edge Cases

Offset arithmetic assumes every referenced field is a `u64` and that offsets are correct for the current `struct hbg_stats` layout. Misuse on non-u64 fields would produce invalid reads/writes.

## Test Signals

Builds with all stats tables and runtime stat values matching expected counters validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_hw.c

## Purpose

This file contains low-level HIBMCGE hardware programming helpers for firmware event handshakes, device spec discovery, IRQ masking/clearing, MAC address/filter programming, MTU/frame sizing, MAC enable, FIFO state, TX/RX descriptor doorbells, link mode changes, pause control, FIFO thresholds, and initial hardware setup.

## Important APIs, Types, and Functions

- `hbg_hw_event_notify()` sends `HBG_HW_EVENT_INIT`, `RESET`, or `CORE_RESET` requests and polls until specs become valid and the request clears.
- `hbg_hw_init()` reads device specs and initializes endian mode, mode-change, RX control, transmit control, and FIFO thresholds.
- `hbg_hw_get_irq_status()`, `hbg_hw_irq_clear()`, `hbg_hw_irq_is_enabled()`, and `hbg_hw_irq_enable()` abstract normal, TX-indirect, and RX-indirect interrupt registers.
- `hbg_hw_set_mtu()`, `hbg_hw_mac_enable()`, `hbg_hw_set_uc_addr()`, `hbg_hw_set_mac_filter_enable()`, `hbg_hw_set_pause_enable()`, `hbg_hw_get_pause_enable()`, and `hbg_hw_set_rx_pause_mac_addr()` implement netdev-facing configuration.
- `hbg_hw_set_tx_desc()` and `hbg_hw_fill_buffer()` write TX descriptors and RX buffer addresses into hardware CFF registers.
- `hbg_hw_adjust_link()` reprograms speed/duplex and waits for MAC-to-PHY link when an external PHY exists.

## Control Flow

Initialization starts with a hardware/firmware event handshake, then reads specification registers into `priv->dev_specs`, derives max frame and RX buffer sizes, and programs PCU/GMAC control registers. Link adjustment disables the MAC, writes port mode and duplex, sends a core-reset event, reenables the MAC, and polls NP link status; repeated NP link failures are scheduled for service-task recovery.

## State and Persistence

The file populates persistent `priv->dev_specs` and writes persistent device registers for IRQ masks, MAC tables, MTU, filters, pause state, RX buffer size, FIFO thresholds, and link mode. `HBG_NIC_STATE_EVENT_HANDLING` serializes firmware event requests.

## Dependencies and Integration Points

It depends on register definitions in `hbg_reg.h`, inline accessors from `hbg_hw.h`, Linux polling helpers, ethtool/if_vlan constants, and service-task scheduling declarations from `hbg_common.h`. It is used by main lifecycle, TX/RX, IRQ, MDIO, ethtool, debugfs, and reset recovery.

## Risks and Edge Cases

Event notification can return `-EBUSY` if another event is in progress and times out after two seconds. Link adjustment ignores the return value from the core-reset event and may reenable the MAC after a failed event. MTU programming toggles a burst-length bit based on `mtu > 2000`, a hardware-specific performance/drop tradeoff. IRQ helpers treat the driver-only TX/RX pseudo-mask bits specially; passing combined masks with those bits and normal bits would only service the first special path.

## Test Signals

Signals include successful device-spec discovery, valid MAC address and MTU range, IRQ enable/disable and clear behavior for normal/TX/RX interrupts, link mode changes for 10/100/1000 SGMII, pause enable get/set, FIFO threshold programming, reset/rebuild register restoration, and NP link-failure scheduling on poll timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_hw.h

## Purpose

This header provides inline HIBMCGE MMIO accessors, bitfield update helpers, and declarations for hardware programming functions.

## Important APIs, Types, and Functions

- `hbg_reg_read()`, `hbg_reg_write()`, `hbg_reg_read64()`, and `hbg_reg_write64()` wrap 32-bit MMIO and lo-hi non-atomic 64-bit MMIO.
- `hbg_reg_read_field()`, `hbg_field_modify()`, and `hbg_reg_write_field()` wrap `FIELD_GET()`/`FIELD_PREP()` register bitfield access.
- Function declarations cover event notify, init, link adjustment, IRQ control, MTU/MAC/filter/pause setup, FIFO occupancy, TX descriptor write, and RX buffer fill.

## Control Flow

The header has no standalone control flow, but `hbg_reg_write_field()` performs a read-modify-write sequence at call sites.

## State and Persistence

No state is stored here. The helpers access persistent device registers through `priv->io_base`.

## Dependencies and Integration Points

It depends on `<linux/bitfield.h>` and `<linux/io-64-nonatomic-lo-hi.h>` and is included by most HIBMCGE modules that touch hardware registers.

## Risks and Edge Cases

Read-modify-write helpers are not locked, so concurrent writers to the same register can lose bits. Non-atomic 64-bit accesses assume the hardware supports lo-hi ordering. Callers must pass masks compatible with `FIELD_PREP()`, including single-bit masks.

## Test Signals

Compile coverage and register-level behavior through hardware init, IRQ operations, MAC filter updates, pause settings, and link changes validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_irq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_irq.c

## Purpose

This file initializes HIBMCGE MSI/MSI-X interrupts, defines IRQ metadata, dispatches TX/RX/error handlers, tracks per-IRQ counters, and schedules recovery work for reset-worthy errors.

## Important APIs, Types, and Functions

- `hbg_irqs[]` maps interrupt names to masks, re-enable behavior, logging, reset requirement, and handler function.
- `hbg_irq_handle()` is the shared IRQ handler for requested vectors.
- `hbg_irq_handle_tx()` and `hbg_irq_handle_rx()` schedule the TX and RX NAPI instances.
- `hbg_irq_handle_err()` logs configured errors and schedules reset when needed.
- `hbg_irq_init()` allocates four PCI vectors, requests three IRQs (`tx`, `rx`, `err`), and allocates stats storage.

## Control Flow

Initialization allocates exactly `HBG_VECTOR_NUM` vectors but intentionally does not request the MDIO vector. The shared handler reads combined hardware status, walks all metadata entries, skips disabled interrupts, disables and clears the current interrupt, increments its counter, invokes the handler, and reenables only entries marked `re_enable`.

## State and Persistence

IRQ metadata is static. Per-device IRQ names, metadata pointers, metadata length, and counters live in `priv->vectors`. Hardware interrupt mask registers persist until changed. Error handlers set service-task state bits for reset.

## Dependencies and Integration Points

The file depends on PCI MSI/MSI-X allocation, devm IRQ requests, hardware IRQ helpers, NAPI in `hbg_ring`, and reset scheduling in `hbg_common.h`. It feeds debugfs and diagnostics through `priv->vectors`.

## Risks and Edge Cases

The driver requires exactly four allocated vectors; systems that can allocate fewer fail probe. All requested vectors use the same handler and scan all interrupt status bits, so hardware vector routing must match expectations. Error interrupts that are not `re_enable` remain disabled after one occurrence unless reset/rebuild reenables them. RX buffer-available immediately reenables itself and increments a software counter.

## Test Signals

Signals include successful allocation of four vectors, requested `tx`, `rx`, and `err` IRQ names, TX/RX NAPI scheduling on interrupts, error logging and reset scheduling for configured bits, accurate debugfs/diagnostic IRQ counters, and clean operation with the unused MDIO vector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_irq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_irq.h

## Purpose

This header declares HIBMCGE IRQ initialization.

## Important APIs, Types, and Functions

It includes `hbg_common.h` and declares `hbg_irq_init(struct hbg_priv *priv)`.

## Control Flow

No control flow is present.

## State and Persistence

No state is declared here.

## Dependencies and Integration Points

The declaration connects main device initialization with the IRQ implementation.

## Risks and Edge Cases

Prototype drift would break probe-time IRQ initialization.

## Test Signals

Build coverage and successful interrupt setup validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_main.c

## Purpose

This file is the main HIBMCGE PCI/netdev driver. It registers the PCI driver, handles probe/shutdown/module lifecycle, initializes hardware/IRQ/MDIO/debugfs/service work, implements netdev operations, manages unicast MAC filters, and coordinates periodic diagnostics/stat updates and reset scheduling.

## Important APIs, Types, and Functions

- `hbg_probe()` allocates the netdev, maps PCI BAR0, initializes hardware subsystems, configures netdev features/ops, sets MTU/MAC/ethtool ops, and registers the netdev.
- `hbg_net_open()` initializes TX/RX rings, enables interrupts and MAC, starts the queue, and starts PHY.
- `hbg_net_stop()` stops PHY/queue/MAC/IRQs, tears down rings, asks hardware to clear TX/RX state, and rebuilds registers.
- `hbg_net_set_mac_address()`, `hbg_net_set_rx_mode()`, and MAC-table helpers manage the hardware unicast filter.
- `hbg_service_task()` handles scheduled error resets, NP link repair, BMC diagnostic pushes, and 30-second stats accumulation.
- `hbg_module_init()` registers debugfs, installs PCI error handlers, and registers the PCI driver.

## Control Flow

Probe allocates `struct hbg_priv` inside the netdev, enables PCI with managed APIs, sets a 32-bit DMA mask, maps BAR0, sends hardware init, initializes IRQs, MDIO/PHY, MAC filter table, delayed work, debugfs, and default pause settings. Netdev open allocates rings before enabling hardware traffic. Netdev stop disables traffic before freeing rings, then resets/rebuilds hardware so RX FIFO references to freed buffers are cleared.

MAC filtering keeps the host MAC at index 0, stores additional unicast addresses in a software table backed by hardware station-address slots, and disables the UC filter when the table overflows or promiscuous mode is requested. MTU changes are rejected while the interface is running.

The service task reschedules itself every second. It handles reset and NP-link-failure bits, pushes diagnostics only when requested, and periodically accumulates 32-bit hardware stats.

## State and Persistence

Persistent state includes netdev features, PCI BAR mapping, `priv->state` bits, MAC table, saved pause settings, stats, delayed work, and hardware register configuration. Device-managed actions clean up delayed work, debugfs subtrees, PHY connection, MDIO bus, IRQs, and netdev registration.

## Dependencies and Integration Points

The file integrates all HIBMCGE modules: hardware, MDIO/PHY, IRQ, TX/RX, ethtool, debugfs, error recovery, diagnostics, and PCI AER. It depends on PCI, netdev, PHYLIB, VLAN constants, unicast filter helpers, RTNL-mediated close/open in reset paths, and module init/exit infrastructure.

## Risks and Edge Cases

`hbg_hw_txrx_clear()` relies on ring teardown happening first; calling it with live buffers would let hardware reference freed memory. MAC filter overflow intentionally disables filtering, increasing received traffic. MTU changes are down-only. The service task starts immediately during probe, so it can run before netdev registration but after core initialization; helpers must tolerate that ordering. `hbg_net_get_stats()` adds `rx_frame_long_err_cnt` twice to `rx_length_errors`, which may overstate that aggregate.

## Test Signals

Signals include PCI probe for Huawei device `0x3730`, BAR0 mapping, netdev registration, open/stop cycles without DMA leaks, MAC address changes and UC filter overflow behavior, promiscuous toggling, down-only MTU changes, periodic stats updates, reset and NP-link service actions, clean shutdown with interface up, and debugfs lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_mdio.c

## Purpose

This file implements HIBMCGE MDIO Clause 22 access, PHY/fixed-PHY setup, PHY link adjustment, pause autonegotiation handling, PHY start/stop wrappers, and retry logic for MAC-to-PHY NP link failures.

## Important APIs, Types, and Functions

- `hbg_mdio_read22()` and `hbg_mdio_write22()` are the `mii_bus` callbacks.
- `hbg_mdio_cmd_send()` formats and starts an MDIO transaction and waits for completion.
- `hbg_mdio_init()` creates/registers the MDIO bus or registers a fixed PHY when `HBG_NO_PHY` is reported.
- `hbg_phy_adjust_link()` maps PHY speed/duplex to HIBMCGE SGMII port mode, calls `hbg_hw_adjust_link()`, and applies flow control.
- `hbg_fix_np_link_fail()` retries PHY stop/start up to five times when MAC NP link stays down.
- `hbg_phy_start()` and `hbg_phy_stop()` wrap PHYLIB operations for netdev open/stop and recovery.

## Control Flow

MDIO initialization reads the device-provided PHY address. If no external PHY exists, it registers a fixed 1 Gbps full-duplex PHY with pause/asym-pause. Otherwise it allocates a devm MDIO bus, masks all PHY addresses except the target, registers the bus, obtains the PHY, initializes the MDIO hardware clock fields, and connects the PHY with SGMII mode. Link adjustment runs from PHYLIB callbacks and only reprograms hardware when link state changes.

## State and Persistence

The file populates `priv->mac.phy_addr`, `mdio_bus`, `phydev`, speed, duplex, autoneg, link status, and pause autoneg fields. Hardware MDIO command registers hold transient operations. Fixed PHY and PHY connections are device-managed.

## Dependencies and Integration Points

It depends on PHYLIB, fixed PHY, MDIO bus registration, RTNL for NP link repair, hardware register helpers, and link/pause helpers from `hbg_hw.c`. It is started/stopped by `hbg_main.c` and used by ethtool PHY operations.

## Risks and Edge Cases

Only Clause 22 operations are implemented. MDIO timeout is one second with 5 ms polling. `hbg_fix_np_link_fail()` dereferences `phydev` and only retries when PHY link is up; repeated failure logs after five attempts and resets the counter. Fixed PHY path bypasses MDIO entirely. Link adjustment ignores unsupported PHY speeds.

## Test Signals

Signals include MDIO bus registration, PHY discovery at the device-provided address, fixed-PHY operation for `HBG_NO_PHY`, link-up/down status prints, correct 10/100/1000 SGMII mode programming, pause autoneg behavior, MDIO timeout handling, and NP-link repair attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_mdio.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_mdio.h

## Purpose

This header declares HIBMCGE MDIO/PHY lifecycle and NP-link repair helpers.

## Important APIs, Types, and Functions

It declares `hbg_mdio_init()`, `hbg_phy_start()`, `hbg_phy_stop()`, and `hbg_fix_np_link_fail()`.

## Control Flow

No control flow is present.

## State and Persistence

No state is declared here.

## Dependencies and Integration Points

The declarations connect main netdev lifecycle and service work to MDIO/PHY implementation.

## Risks and Edge Cases

Prototype mismatch would break probe/open/stop or NP-link service integration.

## Test Signals

Build coverage and PHY lifecycle behavior validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_mdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_reg.h

## Purpose

This header defines the HIBMCGE hardware register map, bitfields, interrupt masks, port modes, and TX/RX descriptor layouts/error-code constants used by all driver modules.

## Important APIs, Types, and Functions

- Register groups cover device specs/events/messages, MDIO, SGMII/GMAC, PCU/FIFO/interrupts, TX/RX buffer channels, stats counters, and descriptor/error fields.
- Interrupt masks include hardware bits such as `WE_ERR`, `RBREQ_ERR`, MAC FIFO errors, AHB errors, drops, buffer availability, TX packet completion, plus driver-only pseudo bits `HBG_INT_MSK_TX_B` and `HBG_INT_MSK_RX_B`.
- Port modes define SGMII 10/100/1000 values.
- `struct hbg_tx_desc` and `struct hbg_rx_desc` represent the hardware descriptor words used by TX/RX and tracepoints.
- RX descriptor field masks and L3/L4 error enums drive receive validation and stats classification.

## Control Flow

There is no runtime control flow. The constants are consumed by register access and descriptor parsing code.

## State and Persistence

No state is stored here. The definitions describe persistent hardware registers and DMA descriptor formats.

## Dependencies and Integration Points

The header is included by hardware, MDIO, IRQ, TX/RX, ethtool, diagnostics, and tracepoint code. It depends on Linux bit macros through transitive includes in consumers.

## Risks and Edge Cases

Register offset or bitfield errors would corrupt device programming or stats interpretation. Driver-only TX/RX pseudo interrupt bits must not be confused with hardware `CF_INTRPT_MSK` bits. Descriptor format definitions must match hardware DMA writes exactly, especially field widths for packet length, port number, checksum errors, and valid size.

## Test Signals

Signals include correct hardware initialization, valid ethtool register dumps, IRQ handling for all masks, RX descriptor trace output matching packets, checksum/stat classification, and successful TX descriptor submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_trace.h

## Purpose

This header defines the HIBMCGE tracepoint used to inspect RX descriptors.

## Important APIs, Types, and Functions

- `TRACE_SYSTEM hibmcge` names the trace subsystem.
- `TRACE_EVENT(hbg_rx_desc, ...)` records PCI name, netdev name, ring index, port number, packet length, valid size, IP offset, VLAN, parse mode, and L2/L3/L4 error codes extracted from `struct hbg_rx_desc`.
- `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE hbg_trace` support tracepoint generation from the local source directory.

## Control Flow

The header contributes tracepoint definitions. `hbg_txrx.c` defines `CREATE_TRACE_POINTS` before including it, and calls `trace_hbg_rx_desc()` for received descriptors.

## State and Persistence

No persistent driver state is stored here. Trace records are emitted only when the tracepoint infrastructure records them.

## Dependencies and Integration Points

It depends on tracepoint APIs, PCI naming, bitfield extraction, and descriptor masks from `hbg_reg.h`. It integrates with RX polling in `hbg_txrx.c`.

## Risks and Edge Cases

Trace field extraction must stay synchronized with descriptor format masks. Tracepoint definitions can affect build output, so only one C file should define `CREATE_TRACE_POINTS`. High-rate RX tracing can be expensive when enabled.

## Test Signals

Signals include successful build of tracepoints, `trace_hbg_rx_desc` availability under ftrace/perf, and trace output matching RX packet descriptors during traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_txrx.c

## Purpose

This file implements HIBMCGE TX/RX data movement: DMA mapping, TX descriptor submission, TX completion recycling, RX page-pool buffer provisioning, RX descriptor validation and stats classification, NAPI pollers, ring allocation, and ring teardown.

## Important APIs, Types, and Functions

- `hbg_net_start_xmit()` is the netdev TX entry point.
- `hbg_napi_tx_recycle()` reclaims completed TX buffers based on hardware-written state.
- `hbg_napi_rx_poll()` refills RX buffers, consumes completed RX descriptors, validates packets, builds SKBs from page-pool pages, and passes packets to GRO.
- `hbg_txrx_init()` and `hbg_txrx_uninit()` allocate/free TX and RX rings for netdev open/stop.
- `hbg_ring_init()`, `hbg_ring_uninit()`, and `hbg_ring_page_pool_init()` manage ring memory, NAPI, and page pool.
- RX helpers classify L2/L3/L4 errors, IP protocol, VLAN, ARP/RARP, multicast/broadcast, checksum status, and drop conditions into `priv->stats`.

## Control Flow

TX checks packet length against the device max frame length, uses `netif_subqueue_maybe_stop()` with ring free space thresholds, maps the SKB linearly, writes completion state to the coherent buffer entry, emits a four-word TX descriptor to hardware registers, advances `ntu` with release semantics, and updates software TX stats. TX NAPI loads `ntu` with acquire semantics, waits for hardware to clear buffer state to complete, unmaps/frees SKBs, advances `ntc`, wakes the queue, completes NAPI, and reenables TX IRQ.

RX ring init creates a page pool and pre-fills hardware RX FIFO. Polling first fills buffers up to FIFO capacity, then checks queued buffers in software order. It syncs page data from device, treats zero packet length as not ready, traces descriptors, builds an SKB with `napi_build_skb()`, validates descriptor fields and checksum state, reserves the driver header area, sets protocol, updates software stats, and submits to GRO. After every consumed buffer it refills one new buffer and advances `ntc`.

## State and Persistence

Rings persist for the interface-open interval. Each `hbg_buffer` tracks SKB/page ownership, DMA address, completion state, and coherent state DMA address. RX page-pool pages are transferred to SKBs with recycle marking. Stats accumulate in `priv->stats` and per-CPU software netstats. Hardware FIFO state persists until `hbg_net_stop()` resets/rebuilds TX/RX state.

## Dependencies and Integration Points

The file depends on netdev queue helpers, DMA API, page pool, NAPI, GRO, tracepoints, hardware register helpers, descriptor definitions, and netdev software stats. It is called from main netdev ops and IRQ handlers.

## Risks and Edge Cases

Only linear SKB TX is mapped; no scatter-gather path is present. TX completion depends on hardware writing `buffer->state` in coherent memory. `hbg_rx_check_l3l4_error()` increments `rx_desc_l3_csum_err_cnt` twice on L3 checksum error, likely overstating that stat. `hbg_ring_page_pool_init()` contains a duplicated `int ret = 0;` line in the source, which would be a compile issue in normal C; if present in the working tree, this needs build validation. RX buffer size/page order calculations must align with device-provided max frame size and page-pool fragment allocation. Ring teardown must happen after IRQ/MAC disable to avoid hardware using freed buffers.

## Test Signals

Signals include successful open/stop ring allocation and teardown, TX queue stop/wake under pressure, TX completion freeing DMA mappings, RX page-pool recycling, checksum-offload behavior with good and bad checksums, descriptor drop/error stats, GRO delivery under traffic, tracepoint emission, DMA mapping failure paths, and no page/SKB leaks across reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_txrx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_txrx.h

## Purpose

This header declares HIBMCGE TX/RX lifecycle and transmit functions and provides inline helpers for frame length, FIFO capacity/fullness, and software ring occupancy.

## Important APIs, Types, and Functions

- `hbg_spec_max_frame_len()` returns TX max frame length or RX buffer size according to direction.
- `hbg_get_spec_fifo_max_num()` returns TX or RX FIFO capacity from device specs.
- `hbg_fifo_is_full()` compares live hardware FIFO occupancy against capacity.
- `hbg_get_queue_used_num()` reads ring `ntu`, `ntc`, and `len` safely enough for diagnostics.
- It declares `hbg_net_start_xmit()`, `hbg_txrx_init()`, and `hbg_txrx_uninit()`.

## Control Flow

No standalone control flow exists. Inline helpers are used by TX/RX, debugfs, and netdev operations.

## State and Persistence

No state is stored here; helpers read `struct hbg_priv` and `struct hbg_ring`.

## Dependencies and Integration Points

The header depends on netdevice/etherdevice declarations and hardware FIFO helpers. It connects `hbg_main.c`, `hbg_irq.c`, and `hbg_debugfs.c` to TX/RX implementation details.

## Risks and Edge Cases

The helpers assume direction is either TX or RX; unexpected combined direction values would select RX in some ternaries. Queue occupancy returns zero when `len` is zero, which is useful for debugfs during teardown.

## Test Signals

Build coverage plus debugfs ring occupancy, TX frame length checks, and RX FIFO full behavior validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hip04_eth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hip04_eth.c

## Purpose

This file implements the Hisilicon P04 Ethernet platform driver. It configures GMAC/PPE registers, manages fixed-size TX descriptors and RX buffers, supports PHY link adjustment for SGMII/MII, handles NAPI RX/TX cleanup, provides TX coalescing ethtool knobs, and registers a platform netdev for `hisilicon,hip04-mac`.

## Important APIs, Types, and Functions

- `struct hip04_priv` holds MMIO bases, PPE syscon regmap, PHY state, NAPI, TX/RX descriptor/buffer arrays, TX coalescing state, and timeout work.
- `hip04_mac_probe()` is the platform probe path.
- `hip04_mac_open()` and `hip04_mac_stop()` start/stop queues, PHY, NAPI, interrupts, and DMA mappings.
- `hip04_mac_start_xmit()` maps one SKB into a TX descriptor, starts hardware TX, updates BQL and stats, and schedules TX cleanup by NAPI or hrtimer.
- `hip04_rx_poll()` reclaims TX and consumes RX descriptors/buffers under NAPI.
- `hip04_config_fifo()`, `hip04_config_port()`, `hip04_mac_enable()`, and `hip04_mac_disable()` program PPE/GMAC hardware.
- `hip04_get_coalesce()` and `hip04_set_coalesce()` expose TX coalescing limits.

## Control Flow

Probe allocates a netdev, maps resources, parses `port-handle` to get port/channel/group, obtains a syscon regmap, reads PHY mode and optional PHY handle, requests the IRQ, initializes TX timeout work and NAPI, resets/configures PPE and GMAC, installs a random MAC address, allocates rings, and registers the netdev.

Open resets software indices and PPE, maps all RX buffers and pushes their DMA addresses to hardware, starts PHY, starts the queue, enables MAC/interrupts, and enables NAPI. TX maps the SKB, fills a hardware descriptor with big-endian fields, writes the descriptor address to PPE, updates BQL/stats, advances `tx_head`, and uses frame-count or timer thresholds to schedule NAPI cleanup. NAPI first reclaims TX descriptors, then consumes RX buffers until budget or hardware says no packet is ready, refilling each slot.

Stop disables NAPI/queue/MAC, forces TX reclaim, resets PPE, stops PHY, and unmaps RX buffers. TX timeout work restarts the interface by stop/open.

## State and Persistence

Runtime state includes descriptor rings, RX fragment pool, DMA mappings, TX head/tail, RX head, remaining RX count, BQL state, coalescing hrtimer settings, PHY link speed/duplex, PPE syscon state, and netdev stats. Hardware configuration persists until reset or driver removal.

## Dependencies and Integration Points

The driver depends on platform devices, OF properties, syscon/regmap, PHYLIB/OF PHY, NAPI, DMA API, hrtimer, netdev BQL, and optional `CONFIG_HI13X1_GMAC` register/layout variants. Kconfig selects `MFD_SYSCON`, `HNS_MDIO`, and `MARVELL_PHY`.

## Risks and Edge Cases

The driver uses many conditional register layouts for HI13X1. `hip04_alloc_ring()` can leak previously allocated RX frags if allocation fails before probe cleanup calls `hip04_free_ring()` with partially initialized data. `hip04_mac_stop()` has a duplicated `int i;` declaration in the source, which needs build validation. RX `build_skb()` consumes preallocated fragments and refill failures can stall RX. TX cleanup relies on hardware clearing descriptor `send_addr`. Timeout recovery runs stop/open from work context.

## Test Signals

Signals include OF probe with valid `port-handle`, syscon, PHY mode and PHY handle; open/close cycles; link changes for SGMII/MII; TX coalescing values accepted/rejected at limits; RX/TX traffic with BQL completions; interrupt error logging for RX/TX drops; TX timeout recovery; and HI13X1/non-HI13X1 build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hip04_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hisi_femac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hisi_femac.c

## Purpose

This file implements the Hisilicon Fast Ethernet MAC platform driver for 10/100 Mbps FEMAC devices. It manages clocks/resets, PHY connection, simple TX/RX software queues, hardware address filtering, NAPI interrupt handling, suspend/resume, and netdev registration for FEMAC-compatible device-tree nodes.

## Important APIs, Types, and Functions

- `struct hisi_femac_priv` holds port/global MMIO bases, clock/reset handles, PHY reset delays, link status, TX/RX queues, FIFO usage, and NAPI.
- `hisi_femac_drv_probe()` and `hisi_femac_drv_remove()` implement platform lifecycle.
- `hisi_femac_net_open()` and `hisi_femac_net_close()` reset/program hardware, manage PHY/NAPI/IRQs, and allocate/free active SKBs.
- `hisi_femac_net_xmit()` submits TX buffers to the hardware enqueue registers.
- `hisi_femac_poll()`, `hisi_femac_rx()`, and `hisi_femac_xmit_reclaim()` handle RX and TX completion.
- `hisi_femac_net_set_rx_mode()` programs promiscuous, multicast, and unicast filtering.
- PM callbacks close/reopen the device around clock disable/enable.

## Control Flow

Probe maps port/global registers, enables the clock, resets MAC and optionally PHY using device-tree delays, connects the PHY, obtains or randomizes the MAC address, sets netdev/NAPI/ethtool ops, initializes port registers and software queues, requests the IRQ, and registers the netdev. Open resets the port, programs host MAC, refills RX input queue while hardware is ready, starts queue/NAPI/PHY, clears IRQ raw bits, and enables interrupts. Interrupts disable the mask and schedule NAPI. NAPI reclaims TX, drains RX packets until budget, acknowledges raw interrupt bits, then reenables interrupts when complete.

## State and Persistence

Software state includes TX/RX circular queues of SKB pointers and DMA addresses, `tx_fifo_used_cnt`, link status, PHY reset delays, and NAPI state. Hardware state includes host MAC, forwarding controls, MAC table filters, FIFO depths, RX coalescing, IRQ masks, and port speed/duplex/link bits.

## Dependencies and Integration Points

The driver depends on platform/OF, clocks, reset controllers, PHYLIB, NAPI, DMA API, netdev filtering helpers, and optional PM. It uses `of_phy_get_and_connect()` and PHY ethtool helpers.

## Risks and Edge Cases

`hisi_femac_free_skb_rings()` has a loop path where a NULL RX/TX SKB logs and continues without advancing `pos`, which would loop indefinitely if the inconsistency occurs. TX submission returns `NETDEV_TX_BUSY` after incrementing drop/fifo error stats when hardware or software queue is full. RX length subtracts FCS and checks against max frame size after `skb_put()`. PHY reset delays must be present when a PHY reset control exists. The PHY reset function sleeps the pre-delay twice before asserting reset, which may be intentional but is unusual.

## Test Signals

Signals include probe for all compatible strings, clock/reset sequencing, PHY link changes updating speed/duplex, RX/TX traffic, queue full handling, multicast/unicast filter limits, promiscuous/allmulti behavior, suspend/resume while running and stopped, and no stuck cleanup loops under fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hisi_femac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hix5hd2_gmac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hix5hd2_gmac.c

## Purpose

This file implements the Hisilicon HIX5HD2/GMAC platform Ethernet driver. It supports GMAC v1/v2 variants, RGMII/MII link programming, hardware MDIO bus registration, four DMA descriptor queues, optional scatter-gather TX descriptors for TSO-capable hardware, NAPI RX/TX completion, clock/reset handling, and platform netdev registration.

## Important APIs, Types, and Functions

- `struct hix5hd2_priv` holds queue descriptors, SG descriptor ring, MMIO bases, SKB arrays, PHY/MDIO state, hardware capabilities, clocks/resets, NAPI, and timeout work.
- `hix5hd2_dev_probe()` and `hix5hd2_dev_remove()` implement platform lifecycle.
- `hix5hd2_net_open()` and `hix5hd2_net_close()` enable clocks, connect/start PHY, initialize hardware, refill RX, enable port/IRQs, and tear down active DMA.
- `hix5hd2_net_xmit()` submits TX descriptors and optional SG descriptors.
- `hix5hd2_poll()`, `hix5hd2_rx()`, and `hix5hd2_xmit_reclaim()` implement NAPI RX/TX processing.
- `hix5hd2_mdio_read()` and `hix5hd2_mdio_write()` implement the embedded MDIO bus.
- `hix5hd2_config_port()` programs RGMII/MII speed/duplex and mode-change registers.

## Control Flow

Probe allocates a netdev, maps MAC/control resources, gets and temporarily enables clocks, resets MAC/PHY, registers an MDIO bus using the device node, reads PHY mode and `phy-handle`, requests the IRQ, obtains or randomizes MAC address, installs ops/features, allocates four coherent descriptor rings and optional SG descriptors, registers NAPI and netdev, then disables clocks until open.

Open enables clocks, connects the PHY, starts PHY, initializes hardware registers and descriptor queue addresses/depths, fills RX free queue, starts queue/NAPI, enables descriptor read/write, enables port TX/RX, and enables interrupts. Interrupts disable IRQs and schedule NAPI. NAPI reclaims completed TX request descriptors, consumes RX back-queue descriptors, refills RX free queue, and reenables IRQs when below budget.

TX uses the hardware TX buffer queue write pointer as the software slot. It refuses to enqueue if `tx_skb[pos]` is still occupied, maps either a linear SKB or SG descriptor table, writes descriptor command/address, memory-barriers descriptor visibility, advances the write pointer, and updates stats/BQL. Timeout work restarts the netdev by close/open.

## State and Persistence

Persistent runtime state includes four coherent descriptor rings, optional SG descriptor ring, RX/TX SKB arrays and DMA mappings, PHY node/MDIO bus, hardware capability flags, link speed/duplex, clocks/resets, and NAPI. Hardware queue pointers and port/register state persist while clocks are enabled.

## Dependencies and Integration Points

The driver depends on platform/OF/property APIs, OF MDIO/PHY, clocks, reset controls, NAPI, DMA API, netdev BQL/stats, and PHY ethtool helpers. Compatible strings map to `GEMAC_V1` or `GEMAC_V2`, with v2 enabling SG feature exposure.

## Risks and Edge Cases

`hix5hd2_fill_sg_desc()` does not unwind already mapped fragments if a later frag map fails, so mapping-failure injection can expose leaks. `hix5hd2_free_dma_desc_rings()` unmaps TX through `tx_rq` descriptors and does not distinguish SG descriptors, which is risky for in-flight SG SKBs on close. The source has duplicated descriptor setup comments and a duplicate `hix5hd2_set_rx_fq()` call, likely harmless. MDIO read treats `MDIO_R_VALID` as an error condition, matching local naming but worth hardware validation. Queue-full handling relies on `tx_skb[pos]` occupancy.

## Test Signals

Signals include probe for all compatible strings, MDIO bus registration and PHY connection, RGMII/MII link mode changes, open/close clock sequencing, RX/TX traffic, SG-fragment TX on v2 hardware, queue-full stop/wake, TX timeout restart, MDIO timeout behavior, and DMA mapping failure tests for linear and SG paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hix5hd2_gmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/Makefile

## Purpose

This Makefile builds the first-generation Hisilicon Network Subsystem support objects and composite drivers.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_HNS) += hnae.o` builds the HNAE framework object.
- `obj-$(CONFIG_HNS_DSAF) += hns_dsaf.o` builds a composite DSAF acceleration-engine object from adapt, GMAC, MAC, misc, main, PPE, RCB, and XGMAC sources.
- `obj-$(CONFIG_HNS_ENET) += hns_enet_drv.o` builds a composite Ethernet driver from `hns_enet.o` and `hns_ethtool.o`.

## Control Flow

There is no runtime control flow. Kbuild links composite objects according to Kconfig.

## State and Persistence

Only build artifacts are affected.

## Dependencies and Integration Points

This file integrates with `CONFIG_HNS`, `CONFIG_HNS_DSAF`, and `CONFIG_HNS_ENET` from the parent Kconfig and groups related HNS implementation files into modules/built-ins.

## Risks and Edge Cases

Composite object lists must stay synchronized with source-level symbol references. Object order can matter for initialization sections and unresolved symbols, so changes need module and built-in build coverage.

## Test Signals

Expected build outputs are `hnae.o`, `hns_dsaf.o` containing all DSAF pieces, and `hns_enet_drv.o` containing ENET plus ethtool support when the corresponding symbols are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/Makefile -->
