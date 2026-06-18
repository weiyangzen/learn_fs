# Research: subset-b-004604

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ll2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ll2.c

## Purpose

`qed_ll2.c` implements the QED driver's "light L2" transport: a small firmware-backed RX/TX queue facility used by non-standard protocol personalities and storage/offload paths rather than the normal Ethernet datapath. It provides both the low-level per-hardware-function connection API declared in `qed_ll2.h` and the public `qed_ll2_ops_pass` vtable consumed through `linux/qed/qed_ll2_if.h`.

The file handles connection allocation, chain allocation, interrupt callback registration, slowpath ramrods for starting/stopping RX and TX queues, RX buffer posting, TX BD construction, completion callbacks, statistics reads, out-of-order TCP helper queues, and the higher-level SKB buffer wrapper used by storage/RDMA/FCoE-style clients.

## Important APIs, types, and functions

The main externally visible low-level APIs are:

- `qed_ll2_acquire_connection(void *cxt, struct qed_ll2_acquire_data *data)`: reserves one of four LL2 connection slots, copies acquisition inputs, validates callback set, allocates RX/TX chains and descriptor tracking arrays, optionally allocates OOO buffers, and registers interrupt callbacks.
- `qed_ll2_establish_connection(void *cxt, u8 connection_handle)`: resets software and hardware chains, initializes descriptor free lists, acquires a core CID, maps the handle to a firmware queue id and stats id, builds doorbell/register producer addresses, starts RX/TX queues through SPQ ramrods, and enables light L2 parser state for non-RDMA/NVMeTCP personalities.
- `qed_ll2_post_rx_buffer()`: places one DMA buffer into the RX BD chain and either queues it in `posting_descq` or notifies firmware immediately through a register write or context-based doorbell.
- `qed_ll2_prepare_tx_packet()` and `qed_ll2_set_fragment_of_tx_packet()`: reserve TX descriptors, fill the start BD and continuation BDs, track fragment DMA addresses for completion callbacks, and ring the TX doorbell once all requested fragments are present.
- `qed_ll2_terminate_connection()` and `qed_ll2_release_connection()`: stop firmware queues, unregister interrupt callbacks, flush active descriptors back through release callbacks, remove protocol filters, release CIDs, free chains/arrays, free OOO coherent buffers, and mark the slot inactive.
- `qed_ll2_get_stats()`: reads LL2 TSTORM/USTORM/PSTORM/port counters into `struct qed_ll2_stats`.
- `qed_ll2_alloc()`, `qed_ll2_setup()`, and `qed_ll2_free()`: allocate, initialize, and release the per-hwfn table of `struct qed_ll2_info`.

The public interface vtable `qed_ll2_ops_pass` exposes `start`, `stop`, `start_xmit`, `register_cb_ops`, and `get_stats`. It is the higher-level API used by protocol drivers. It allocates a `struct qed_cb_ll2_info` with `qed_ll2_alloc_if()` from `qed_main.c` slowpath startup and deallocates it via `qed_ll2_dealloc_if()`.

Important local data structures include:

- `struct qed_cb_ll2_info`: the client-facing LL2 state stored at `cdev->ll2`; it tracks a selected connection handle, RX buffer size/count, a spinlock-protected list of allocated `qed_ll2_buffer` entries, and optional client callbacks/cookie.
- `struct qed_ll2_buffer`: SKB backing storage plus DMA address for the wrapper RX path.
- `struct qed_ll2_info`: declared in `qed_ll2.h`; the per-connection slot containing acquisition input, CID, queue id, stats id, state, callbacks, and RX/TX queue objects.
- `struct qed_ll2_rx_queue`: RX and completion chains, producer address, doorbell data, and active/free/posting descriptor lists.
- `struct qed_ll2_tx_queue`: TX chain, doorbell data, active/free/sending descriptor lists, current in-flight construction state, and completion bookkeeping.
- `struct qed_ll2_rx_packet` and `struct qed_ll2_tx_packet`: software descriptors that mirror chain entries and carry cookies/DMA information back to callbacks.

## Control flow

Low-level connection setup starts with `qed_ll2_acquire_connection()`. It divides handles into legacy RAM-based queues and context-based queues via `_qed_ll2_calc_allowed_conns()`, then finds an inactive slot under that slot's mutex. It marks the slot active before heavy allocation, copies inputs, translates the requested TX destination to firmware enum values, clamps `tx_max_bds_per_packet`, validates callbacks, allocates RX chains and RX software descriptors, allocates TX chains and variable-sized TX packet descriptors, and allocates extra coherent OOO buffers when `conn_type == QED_LL2_TYPE_OOO`. It then registers RX/TX completion callbacks with the interrupt layer, selecting special loopback/OOO completion handlers for OOO connections.

`qed_ll2_establish_connection()` is the second stage. It takes a PTT, verifies the active handle, resets chains, builds RX and TX descriptor free lists, clears firmware consumer indexes, acquires a core CID, clears the core context memory, maps the handle to a firmware queue id with `qed_ll2_handle_to_queue_id()`, and computes a TX stats id with `qed_ll2_handle_to_stats_id()`. Legacy RX queues use a GTT-mapped TSTORM producer register; context-based queues set `ctx_based`, use the hwfn doorbell window, and fill `core_pwm_prod_update_data`. TX always uses a CID-derived doorbell address and `core_db_data`. It starts RX through `qed_sp_ll2_rx_queue_start()`, starts TX through `qed_sp_ll2_tx_queue_start()`, may set `PRS_REG_USE_LIGHT_L2`, initializes OOO queue state, and installs LLH FCoE/FIP protocol filters for FCoE.

RX posting is descriptor-list driven. `qed_ll2_post_rx_buffer()` takes a free `qed_ll2_rx_packet`, produces one RX BD and one RCQ entry, fills DMA address/buffer length/cookie, and either places the descriptor on `posting_descq` or calls `qed_ll2_post_rx_buffer_notify_fw()`. Notification drains `posting_descq`, moves descriptors to `active_descq`, calculates BD/CQE producers, executes `dma_wmb()`, and writes either a 64-bit context doorbell or a 32-bit legacy producer register.

RX completion starts in `qed_ll2_rxq_completion()`, which checks `b_cb_registered`, reads the firmware CQ consumer, consumes CQEs until the software index catches up, and dispatches slowpath CQEs to `qed_ll2_handle_slowpath()` or regular/GSI CQEs to `qed_ll2_rxq_handle_completion()`. Regular completion removes the oldest active RX descriptor, parses CQE fields through `qed_ll2_rxq_parse_reg()` or `qed_ll2_rxq_parse_gsi()`, consumes the RX chain entry, moves the descriptor back to `free_descq`, unlocks, invokes `rx_comp_cb`, and re-locks. The wrapper callback `qed_ll2b_complete_rx_packet()` validates length, allocates a replacement buffer, builds an SKB with `slab_build_skb()`, reserves placement offset plus `NET_SKB_PAD`, sets protocol from the Ethernet header, attaches VLAN tag when present, calls the registered client `rx_cb`, and reposts the replacement or reused buffer.

TX submission starts in `qed_ll2_prepare_tx_packet()`. It validates handle and max BD count, requires no partially built packet, selects a free software TX packet and sufficient chain space, records the packet cookie/BD count/first fragment through `qed_ll2_prepare_tx_packet_set()`, fills the start BD and reserves continuation BDs in `qed_ll2_prepare_tx_packet_set_bd()`, then calls `qed_ll2_tx_packet_notify()`. Notification is deferred until `cur_send_frag_num == bd_used`; once complete, the packet moves to `sending_descq`, and if the packet's `notify_fw` flag is set all sending packets move to `active_descq`, `spq_prod` is updated, `wmb()` orders BD writes, and the TX doorbell is written. Additional fragments are filled by `qed_ll2_set_fragment_of_tx_packet()`, which updates reserved continuation BDs and then retries notification.

TX completion is handled by `qed_ll2_txq_completion()`. It computes completed BDs from the firmware consumer and software `bds_idx`, walks packets from `active_descq`, ensures the completed BD count covers each packet, consumes chain BDs, returns the software descriptor to `free_descq`, temporarily unlocks, and calls `tx_comp_cb`. The wrapper `qed_ll2b_complete_tx_packet()` unmaps the first SKB fragment, calls the external `tx_cb` when registered, and frees the SKB. There is a notable asymmetry: the wrapper maps `skb->data` with `skb->len` but unmaps with `skb_headlen(skb)`, while additional fragments mapped by `skb_frag_dma_map()` are not individually unmapped by the wrapper callback because only the first fragment address is passed through `tx_comp_cb` for each packet-level completion. This deserves careful validation if the source mirrors production code.

OOO/lb control flow uses `qed_ll2_lb_rxq_completion()` and `qed_ll2_lb_txq_completion()`. RX CQEs carry TCP event opcodes in opaque data. The handler updates OOO history/isle structures, consumes RX descriptors into `qed_ooo_buffer` instances for create/add/join/peninsula events, deletes isles when requested, submits new RX buffers from the OOO free list, and submits ready buffers back through LL2 TX. TX completions recycle OOO buffers back into RX posting or the free list. `qed_ll2_start_ooo()` creates a dedicated loopback LL2 queue for iSCSI/NVMeTCP personalities.

The public wrapper start path is `qed_ll2_start()`. It validates the LL2 MAC, initializes the client buffer list and lock, computes RX buffer size from DMA pad, Ethernet header, cache line, and MTU, allocates `QED_LL2_RX_SIZE` buffers or twice that when a storage PF is affinitized to engine 1 in CMT, then calls `__qed_ll2_start()` for the affinitized hwfn and possibly the leading hwfn. It may start a dedicated OOO queue, install an LLH MAC filter except for NVMeTCP, and stores `ll2_mac_address`. Stop reverses that through `qed_ll2_stop()`, queue termination/release, OOO stop, LLH filter removal, buffer cleanup, and handle reset.

## State and persistence behavior

State is in memory and hardware/firmware contexts only; the file does not persist data to disk. Persistent device configuration is not written here except transient LLH filters and firmware queue state.

Key state transitions:

- Connection slots in `p_hwfn->p_ll2_info[]` move inactive -> active in `qed_ll2_acquire_connection()` and active -> inactive in `qed_ll2_release_connection()`.
- `cdev->ll2` exists only while slowpath has allocated the LL2 public interface; its `handle` is set by `qed_ll2_start()` and reset to `QED_LL2_UNUSED_HANDLE` on stop/failure.
- RX descriptors move among `free_descq`, `posting_descq`, and `active_descq`; TX descriptors move among `free_descq`, `sending_descq`, and `active_descq`.
- Hardware producer/consumer state is tracked by `qed_chain` producer/consumer indexes and firmware consumer pointers registered through the interrupt layer.
- Doorbell recovery state is registered for TX queue doorbells and context-based RX producer doorbells; stop paths remove those registrations.
- OOO state lives in `p_hwfn->p_ooo_info` and is flushed/released on establish/terminate/release.

Concurrency control uses per-connection mutexes for slot active state, RX/TX spinlocks for descriptor lists and chain manipulation, and bottom-half-safe locking for the wrapper's RX buffer list. Completion paths deliberately drop queue spinlocks before invoking external callbacks.

## Dependencies and integration points

This file depends on QED core infrastructure: `qed_chain`, `qed_int_register_cb()`, `qed_spq_post()`, `qed_cxt_acquire_cid()`, `qed_ptt_acquire()`, `qed_wr()`, `qed_llh_*_filter()`, `qed_db_recovery_add()/del()`, and MCP/register definitions. It uses Linux DMA mapping, SKB allocation/building, VLAN helpers, spinlocks/mutexes, and PCI device DMA APIs.

Integration with `qed_main.c` is direct. `qed_main.c` includes `qed_ll2.h`, allocates `cdev->ll2` in `qed_slowpath_start()` when any hwfn has `using_ll2`, and deallocates it in `qed_slowpath_stop()`. Protocol drivers get `qed_ll2_ops_pass`, register callbacks, start LL2 with `struct qed_ll2_params`, transmit SKBs through `start_xmit`, and collect stats through `get_stats`.

The storage/offload integration is personality-sensitive: FCoE uses FCoE/FIP filters and `QED_LL2_TYPE_FCOE`, iSCSI/NVMeTCP use TCP ULP plus OOO queue setup, RDMA uses ROCE/IWARP connection types and special interrupt-vector allocation in `qed_main.c`.

## Risks and edge cases

- Error unwind in `qed_ll2_acquire_connection()` always returns `-ENOMEM` from `q_allocate_fail`, even for validation or chain allocation errors with different codes.
- `qed_ll2_acquire_connection()` marks a slot active before all validation. The cleanup path calls release, but any early `return -EINVAL` after `tx_dest` translation failure bypasses `q_allocate_fail` and can leave the slot active if an invalid `tx_dest` is supplied after a slot has been marked active.
- `qed_ll2_txq_completion()` sets `b_completing_packet = true`; some error exits before the final reset may leave it true and future completions return `-EBUSY`.
- `qed_ll2_rxq_completion()` computes `b_last_cqe` before consuming the CQE, so it appears to compare the old software index to the firmware index and may not mark the final CQE as expected.
- The wrapper TX DMA mapping/unmapping path should be audited for fragmented SKBs. The first mapping is for `skb->len`; completion unmaps `skb_headlen(skb)`, and continuation fragment mappings are not obviously unmapped.
- `qed_ll2_stop()` removes the LLH MAC filter twice for non-NVMeTCP paths: once conditionally and once unconditionally.
- Callback invocation outside locks prevents deadlocks but means callbacks can race with stop/release unless `b_cb_registered`, interrupt unregister, and queue flushing order is correct.
- Statistics use fixed firmware memory offsets and disable TX stats only when computed stats id is invalid; tests should cover context-based queue ids near counter limits.

## Test signals

Useful validation signals include successful slowpath startup for FCoE/iSCSI/NVMeTCP/RDMA personalities, LL2 start/stop cycles with no leaked DMA mappings, RX buffer refill under allocation failure, TX completion for single-fragment and multi-fragment SKBs, OOO queue traffic and teardown for iSCSI/NVMeTCP, CMT storage engine-1 start/stop where LL2 is also started on engine 0, LLH filter add/remove behavior, doorbell recovery registration and deletion, and `qed_ll2_get_stats()` values for legacy and context queues. Kernel dynamic debug around `QED_MSG_LL2`, DMA API debugging, KASAN/KMSAN, lockdep, and fault injection in `qed_chain_alloc()`, DMA mapping, `qed_ptt_acquire()`, and SPQ posts would catch many of the high-risk paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ll2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ll2.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ll2.h

## Purpose

`qed_ll2.h` is the internal header for the QED light-L2 implementation. It defines the per-connection data structures used by `qed_ll2.c`, declares the low-level LL2 lifecycle/data-path/stat APIs, and exposes the public `qed_ll2_ops_pass` vtable for protocol-facing code.

The header is not the external consumer ABI; it includes `linux/qed/qed_ll2_if.h` for public parameter/callback/stat types and then defines driver-private queue and descriptor state around those public types.

## Important APIs, types, and constants

Connection capacity constants define a small fixed table:

- `QED_MAX_NUM_OF_LL2_CONNECTIONS` is 4.
- `QED_MAX_NUM_OF_LL2_CONNS_PF` is 4.
- `QED_MAX_NUM_OF_LEGACY_LL2_CONNS_PF` is 3.
- `QED_MAX_NUM_OF_CTX_LL2_CONNS_PF` is one context-based queue.
- `QED_LL2_LEGACY_CONN_BASE_PF` starts at 0.
- `QED_LL2_CTX_CONN_BASE_PF` starts after the legacy region.

`struct qed_ll2_rx_packet` is the software descriptor corresponding to an RX BD. It stores list linkage, the produced RX BD pointer, DMA address, buffer length, callback cookie, placement offset, parse flags, packet length, VLAN, and two opaque data words copied from firmware CQEs.

`struct qed_ll2_tx_packet` is the software descriptor corresponding to a TX packet. It has list linkage, BD count, a notify flag, a callback cookie, and a flexible array `bds_set[]` sized at allocation time by `tx_max_bds_per_packet`; each fragment slot stores a TX BD pointer, DMA address, and length.

`struct qed_ll2_rx_queue` owns RX queue synchronization and hardware state:

- `lock` protects RX chain and descriptor-list mutation.
- `rxq_chain` is the produced RX BD chain.
- `rcq_chain` is the consumed RX completion chain.
- `rx_sb_index` and `p_fw_cons` are assigned by interrupt callback registration.
- `ctx_based` selects context-doorbell vs legacy producer-register notification.
- `b_cb_registered` gates completion processing.
- `active_descq`, `free_descq`, and `posting_descq` represent buffers owned by firmware, available to software, and staged for later notification.
- `set_prod_addr` and `db_data` carry producer notification target/state.

`struct qed_ll2_tx_queue` owns TX queue synchronization and hardware state:

- `lock` protects TX chain, descriptor lists, and partial packet construction.
- `txq_chain` is the TX BD chain.
- `tx_sb_index`, `p_fw_cons`, `doorbell_addr`, and `db_msg` connect to interrupt and doorbell hardware.
- `active_descq`, `free_descq`, and `sending_descq` represent packet descriptors visible to firmware, reusable by software, and complete-but-not-yet-doorbelled.
- `cur_send_packet`/`cur_send_frag_num` track a partially filled multi-BD packet.
- `cur_completing_packet`/`cur_completing_bd_idx`/`cur_completing_frag_num`/`b_completing_packet` track completion progress.
- `descq_mem` stores the contiguous variable-sized `qed_ll2_tx_packet` descriptor pool.

`struct qed_ll2_info` is the per-connection slot:

- `mutex` protects active state changes.
- `input` preserves `struct qed_ll2_acquire_data_inputs` for later queue start and behavior decisions.
- `cid`, `my_id`, `queue_id`, `tx_stats_id`, `tx_dest`, `tx_stats_en`, and `main_func_queue` mirror firmware context/queue identity.
- `b_active` marks slot ownership.
- `cbs` stores required completion/release callbacks.
- `rx_queue` and `tx_queue` contain the queue state.

Declared functions cover lifecycle (`qed_ll2_alloc`, `qed_ll2_setup`, `qed_ll2_free`, `qed_ll2_acquire_connection`, `qed_ll2_establish_connection`, `qed_ll2_terminate_connection`, `qed_ll2_release_connection`), datapath (`qed_ll2_post_rx_buffer`, `qed_ll2_prepare_tx_packet`, `qed_ll2_set_fragment_of_tx_packet`), and stats (`qed_ll2_get_stats`).

## Control flow encoded by the API shape

The API enforces a two-phase connection setup. Callers first call `qed_ll2_acquire_connection()` to reserve a handle and allocate queues, then `qed_ll2_establish_connection()` to start firmware queues. RX buffers can be posted only after establish has built `set_prod_addr`; TX packets can be prepared only once TX chains and doorbells are initialized. Teardown is also two-phase: `qed_ll2_terminate_connection()` stops firmware-visible queues and flushes descriptors, then `qed_ll2_release_connection()` frees allocations and marks the handle inactive.

The TX API models multi-fragment packets explicitly. The first fragment and packet-level metadata are submitted with `qed_ll2_prepare_tx_packet()`, and additional fragments are appended by repeated `qed_ll2_set_fragment_of_tx_packet()` calls until `num_of_bds` is satisfied. This is why `struct qed_ll2_tx_queue` stores a current send packet and fragment cursor.

The RX API leaves buffer allocation to the caller. `qed_ll2_post_rx_buffer()` accepts a DMA address, length, cookie, and a `notify_fw` flag. The cookie is returned through completion/release callbacks so higher layers can own SKBs, OOO buffers, or protocol-specific buffer objects.

## State and persistence behavior

All declarations describe volatile driver state. The structures persist only for the lifetime of a `struct qed_hwfn`, `struct qed_dev`, or active LL2 connection. No disk persistence is defined. Hardware/firmware state associated with these structures is managed by implementation functions in `qed_ll2.c`.

Ownership is split deliberately:

- The connection table is stored on `struct qed_hwfn` as `p_ll2_info`.
- Public LL2 wrapper state is stored on `struct qed_dev` as `cdev->ll2` and is allocated/deallocated by `qed_ll2_alloc_if()`/`qed_ll2_dealloc_if()` in the implementation.
- External protocol callbacks and public parameter structures come from `qed_ll2_if.h`; this header stores them internally but does not define their public ABI.

## Dependencies and integration points

The header includes Linux core types, list, mutex, slab, spinlock, `qed_chain`, and public LL2 interface definitions. It also includes `qed.h`, `qed_hsi.h`, and `qed_sp.h`, binding the LL2 interface to QED hardware/software queue formats and slowpath request infrastructure.

`qed_main.c` includes this header so slowpath startup can allocate the public LL2 interface and so the core common ops can coexist with LL2 support. `qed_ll2.c` is the primary implementation consumer. Other QED protocol code interacts mostly through the external `qed_ll2_ops_pass` and public `qed_ll2_if.h` types.

## Risks and edge cases

- The header fixes maximum LL2 connection count at four and partitions only one context-based queue. New firmware queue types or additional context queues would require coordinated constant and mapping changes.
- `struct qed_ll2_tx_packet` uses a flexible array and is allocated as a custom stride in `qed_ll2.c`; any copy, stack allocation, or `sizeof` misuse would be wrong.
- Queue list fields require strict initialization before use. The header alone does not encode which lists are valid before establish.
- `p_fw_cons` is a pointer filled by interrupt registration; completion functions require it to be valid when `b_cb_registered` is true.
- `ctx_based` changes the producer notification width and recovery registration behavior. Tests should exercise both legacy and context-based RX queues.

## Test signals

Compile-time signals include structure layout compatibility with firmware BD/CQE definitions and successful build under configurations with LL2, storage, RDMA, and SR-IOV enabled. Runtime signals include successful handle allocation across legacy/context ranges, correct behavior at connection-table exhaustion, queue start with RX-only or TX-only descriptor counts, and safe teardown with active descriptors. Static-analysis focus should include flexible-array allocation arithmetic, list ownership, callback pointer validation, and locking expectations around the queue structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ll2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_main.c

## Purpose

`qed_main.c` is the central core-module glue for the QLogic/Marvell FastLinQ 4xxxx QED driver. It initializes module-level link-mode maps, probes and removes core devices, owns PCI BAR/DMA setup, configures interrupt modes, starts and stops the slowpath, exposes the `qed_common_ops_pass` vtable to protocol drivers, translates link configuration/status between MFW and Linux-facing structures, handles firmware/NVM flashing helpers, schedules recovery and management TLV work, and allocates/deallocates LL2 interface state when protocol personalities need light-L2 support.

The file is not a Linux `pci_driver` registration by itself in this snapshot; instead it exports operations that upper protocol-specific QED clients call through common ops.

## Important APIs, types, and functions

Module initialization:

- `qed_init()` prints the core module version and calls `qed_mfw_speed_maps_init()`.
- `qed_mfw_speed_map_populate()` and `qed_mfw_speed_maps_init()` convert static arrays of ethtool link-mode bit numbers into `link_mode` masks stored in `qed_mfw_ext_maps[]` and `qed_mfw_legacy_maps[]`.
- `MODULE_FIRMWARE(QED_FW_FILE_NAME)` declares the zipped init-values firmware file derived from firmware version macros.

Device lifecycle:

- `qed_alloc_cdev()` allocates and initializes `struct qed_dev`.
- `qed_init_pci()` enables the PCI device, validates BARs, requests regions, sets bus mastering, saves PCI state, checks revision and PCIe capability, sets 64-bit DMA mask, maps BAR0 registers, and maps BAR2 doorbells for PFs.
- `qed_free_pci()` unmaps doorbells/registers, releases regions when appropriate, and disables the PCI device.
- `qed_probe()` allocates `qed_dev`, sets protocol/VF/recovery/debug state, initializes PCI, and calls `qed_hw_prepare()`.
- `qed_remove()` reverses through `qed_hw_remove()`, PCI cleanup, power-state callback, and device free.

Slowpath and resource lifecycle:

- `qed_nic_setup()` marks non-Ethernet personalities as `using_ll2`, allocates resources, and performs resource setup.
- `qed_slowpath_start()` starts IOV and slowpath workqueues, loads firmware for PFs, acquires an aRFS PTT on single-hwfn PFs, allocates resources, configures interrupts, allocates zlib streams, initializes debug, starts hardware through `qed_hw_init()`, allocates `cdev->ll2` when any hwfn needs LL2, sends driver version to MFW, and resets vport stats.
- `qed_slowpath_stop()` stops workqueues, deallocates LL2 public state, releases PTT/stream/SR-IOV resources, stops hardware/tasklets/debug, frees IRQs/MSI-X, frees resources/IOV workqueue, and releases firmware.
- `qed_nic_stop()` calls `qed_hw_stop()`, disables SP tasklets, and exits PF debug state.

Interrupt handling:

- `qed_set_int_mode()` selects MSI-X, MSI, or INTa with fallback unless forced.
- `qed_enable_msix()` handles vector count negotiation and VF exact-vector requirements.
- `qed_slowpath_setup_int()` calculates requested slowpath/fastpath MSI-X vectors for PFs, handles kdump reduction, and partitions RDMA vectors away from L2 queues.
- `qed_slowpath_vf_setup_int()` configures VF MSI-X counts from VF queue information.
- `qed_slowpath_irq_req()`, `qed_slowpath_irq_sync()`, and `qed_slowpath_irq_free()` request/synchronize/free IRQs.
- `qed_single_int()` dispatches shared INTa/MSI slowpath and up to 64 fastpath handlers per hwfn.
- `qed_simd_handler_config()` and `qed_simd_handler_clean()` install/remove fastpath callback tokens.

Slowpath workqueue:

- `qed_slowpath_wq_start()` and `qed_slowpath_wq_stop()` manage per-hwfn workqueues for PFs.
- `qed_slowpath_delayed_work()` sets `slowpath_task_flags` with memory barriers and queues delayed work.
- `qed_slowpath_task()` processes MFW TLV requests and periodic doorbell recovery under a PTT, rescheduling if the PTT is unavailable.
- `qed_periodic_db_rec_start()` starts bounded periodic doorbell recovery.
- `qed_mfw_tlv_req()` queues immediate TLV processing.

Link and capability handling:

- `qed_set_link()` translates `struct qed_link_params` overrides into MCP link params, including legacy and extended speed advertisements, forced speeds, pause, loopback, EEE, and FEC, then calls `qed_mcp_set_link()`.
- `qed_set_ext_speed_params()` handles extended MFW speed and FEC encodings for 25/40/50/100G.
- `qed_get_link_data()` gathers link params/state/caps from MCP for PFs or VF bulletin paths for VFs.
- `qed_fill_link_capability()` maps media type, transceiver type, speed mask, and board config into phylink capability bits.
- `qed_fill_link()` fills `struct qed_link_output`, including link up/speed, supported/advertised/partner capabilities, pause, FEC, port, autoneg, and EEE.
- `qed_get_current_link()`, `qed_link_update()`, and `qed_bw_update()` expose link/bandwidth updates to protocol callbacks and VFs.

NVM/firmware helpers:

- `qed_nvm_flash()` loads a firmware file and interprets a QED NVM batch format.
- `qed_nvm_flash_image_validate()` validates signature, size, and max command id.
- `qed_nvm_flash_image_file_start()` and `qed_nvm_flash_image_file_data()` submit file upload chunks through MCP NVM writes.
- `qed_nvm_flash_image_access()` applies masked writes to NVM images or recalculates/writes image CRC via `qed_nvm_flash_image_access_crc()`.
- `qed_nvm_flash_cfg_write()`, `qed_nvm_flash_cfg_len()`, and `qed_nvm_flash_cfg_read()` write/read MFW NVM config attributes.
- `qed_nvm_get_image()` delegates image reads to MCP.

Common ops and callbacks:

- `qed_common_ops_pass` is the main exported vtable. It includes selftests, probe/remove, slowpath start/stop, interrupt info, SB init/release, link ops, debug/devlink, chain allocation, NVM flashing, coalescing, LED, recovery, PF updates, doorbell recovery, EEPROM reads, GRC config, MFW reports, SB debug, and ESL status.
- `qed_fill_dev_info()` fills `struct qed_dev_info` with PCI, tunnel, firmware, MFW, flash, WOL, ESL, SmartAN, RDMA, MAC, and MTU data.
- `qed_get_protocol_stats()` returns LAN/FCoE/iSCSI stats for MFW.
- `qed_mfw_fill_tlv_data()` fills generic or protocol TLV data for management firmware using protocol callbacks.
- `qed_hw_error_occurred()` and `qed_schedule_recovery_handler()` bridge hardware error/recovery notifications to protocol callbacks.

## Control flow

Probe begins with `qed_probe()`. It allocates a zeroed `qed_dev`, initializes common fields with `qed_init_struct()`, sets Linux driver type, protocol, VF flag, debug settings, and recovery state, then calls `qed_init_pci()`. PCI setup enables the device, checks BAR0 and PF BAR2, requests regions when the PCI enable count indicates first enable, enables bus mastering, saves state, rejects invalid revision id and non-PCIe devices, sets a 64-bit coherent DMA mask, maps BAR0 into `regview`, captures BAR2 doorbell physical/size, and maps doorbells write-combined for devices with BAR2. After PCI, `qed_hw_prepare()` initializes hardware-function structures and device metadata.

Slowpath start is the major bring-up sequence. `qed_slowpath_start()` first starts SR-IOV and per-hwfn slowpath workqueues. PFs request the versioned firmware blob and may acquire a PTT for aRFS. `qed_nic_setup()` marks non-Ethernet personalities as using LL2, allocates driver resources, and sets them up. Interrupt setup then selects PF or VF paths. PFs allocate zlib inflate streams so zipped firmware init data can be decompressed by `qed_unzip_data()`, and debug PF state is initialized. The function builds tunnel defaults, driver load params, and `qed_hw_init_params`, calls `qed_hw_init()`, sets tunnel feature masks, allocates `cdev->ll2` if `using_ll2`, sends driver version to MFW, and resets stats. The error path unwinds in reverse: LL2 dealloc, hardware stop/timer stop, IRQ free, stream free, MSI-X disable, resource free, firmware release, aRFS PTT release, IOV stop, and workqueue stop.

Slowpath stop reverses normal startup. It stops slowpath workqueues first to prevent new delayed work, frees the LL2 public object, releases aRFS PTT and zlib streams for PFs, disables SR-IOV for Ethernet PFs, calls `qed_nic_stop()`, frees slowpath IRQs, disables MSI/MSI-X, frees resources, stops IOV workqueues, and releases firmware.

Interrupt mode selection starts from requested mode. MSI-X allocates an `msix_table`, calls `qed_enable_msix()`, and falls through to MSI/INTa only if not forced. MSI is allowed only for single-hwfn devices. INTa is final fallback. Shared/single interrupt dispatch reads SISR per hwfn, schedules the slowpath tasklet for bit 0, and calls registered fastpath handlers for subsequent bits.

Link setting for PFs acquires a PTT on hwfn 0, edits the MCP link params in place according to override flags, uses speed maps to convert Linux ethtool link-mode masks into MFW bitfields, optionally fills extended speed/FEC fields, and calls `qed_mcp_set_link()`. For VFs it does not modify hardware and instead schedules a forced link query. Link reporting pulls MCP or VF bulletin state, maps media/transceiver/speed/board state into phylink masks, fills pause/FEC/EEE/autoneg/current speed fields, informs VFs, and calls the protocol `link_update` callback only from the leading hwfn.

NVM flashing parses a binary command stream. After validation, the loop reads a 32-bit command id and advances a `const u8 *data` cursor through command-specific parsers. Some commands set `check_resp`, after which `qed_nvm_flash()` fetches an MCP response and accepts only OK response codes. Config writes batch commits every `QED_NVM_CFG_MAX_ATTRS` attributes and use `QED_NVM_CFG_OPTION_INIT/COMMIT/FREE` flags.

## State and persistence behavior

Most state is runtime driver state stored in `struct qed_dev` and per-hwfn structures:

- PCI mappings: `cdev->regview`, `cdev->doorbells`, `db_phys_addr`, `db_size`, and `pci_params`.
- Interrupt state: `cdev->int_params`, MSI-X table, fastpath initialized flag, RDMA vector partitioning, tasklet requested/enabled flags, and SIMD fastpath handlers.
- Slowpath work state: per-hwfn `slowpath_wq`, `slowpath_task`, `slowpath_wq_active`, `slowpath_task_flags`, and periodic doorbell recovery counter.
- Firmware/debug state: `cdev->firmware`, per-hwfn zlib `stream`, debug PF state, aRFS PTT, and tunnel feature mask.
- Protocol state: `protocol`, `protocol_ops`, `ops_cookie`, `common_dev_info`, `ll2`, and `ll2_mac_address`.
- Recovery state: `recov_in_prog` and protocol-scheduled recovery/error callbacks.

Persistent device state can be changed through MCP operations in this file: NVM image writes, NVM config writes, wake-on-LAN/current configuration updates, MAC/MTU/driver-state overrides, LED mode, and link settings. Those operations are mediated by PTT acquisition and MCP helpers, not local disk writes.

The module-level speed maps are initialized once at module load. They use `__ro_after_init` map storage and discard original `__initconst` arrays after converting them into link-mode masks.

## Dependencies and integration points

The file integrates kernel PCI, DMA, IRQ, workqueue, firmware loading, zlib, ethtool link modes, phylink, devlink, CRC32, and crash dump APIs. It depends heavily on QED internal modules: hardware init/remove, resources, interrupts, MCP, SR-IOV, slowpath queue, LL2, FCoE, iSCSI, selftests, debug, devlink, and register definitions.

The LL2 integration point is important for this work item. `qed_nic_setup()` sets `p_hwfn->using_ll2 = true` for non-Ethernet personalities. Later `qed_slowpath_start()` calls `qed_ll2_alloc_if(cdev)` if the leading hwfn uses LL2; `qed_slowpath_stop()` calls `qed_ll2_dealloc_if(cdev)`. The actual LL2 queue start/stop and data-path operations are exported from `qed_ll2.c` through `qed_ll2_ops_pass`.

The common ops vtable is the core boundary to protocol drivers such as Ethernet, FCoE, iSCSI, RDMA, and management tooling. Protocol drivers call `probe`, `slowpath_start`, `get_fp_int`, `sb_init`, `set_link`, `nvm_flash`, and related functions through this table. The reverse callback boundary is `protocol_ops.common` and `ops_cookie`, used for link updates, bandwidth updates, recovery scheduling, hardware error scheduling, and TLV data collection.

## Risks and edge cases

- `qed_init_pci()` has direct `return -EINVAL`/`return -ENOMEM` paths after BAR mappings that bypass the shared `err2` unwind labels, which can leak earlier PCI resources or mappings if doorbell setup fails.
- Several NVM parser functions read unaligned little-endian fields via raw casts such as `*((u32 *)*data)` and `*((u16 *)*data)`. This is sensitive to alignment, endian assumptions, and bounds; validation checks total image size but individual command parsers do not visibly guard every cursor advance.
- `qed_set_link()` returns `-ENODATA` when `qed_mcp_get_link_params()` fails but does not release the acquired PTT before that return.
- `qed_alloc_stream_mem()` can return after partial allocation without freeing already allocated stream/workspace objects; the later global cleanup may handle some paths but direct failure accounting should be audited.
- `qed_free_stream_mem()` returns when it finds a hwfn without `stream`, potentially skipping later hwfns if partial allocation state is sparse.
- `qed_slowpath_start()` has many cross-module allocations and an intricate error unwind; changes should verify every acquisition has exactly one release on every failure path.
- Interrupt vector partitioning for RDMA depends on feature counts and hwfn count. Off-by-one or odd MSI-X counts can affect fastpath/RDMA vector exposure.
- Link capability mapping depends on MCP media/transceiver values and fallback speed masks. Unknown media defaults can under-report capabilities.
- `qed_fill_generic_tlv_data()` sets `rx_bytes_set = true` twice, likely intending `tx_bytes_set` for the TX byte counter.

## Test signals

Strong test coverage signals include PF and VF probe/remove cycles, slowpath start/stop under Ethernet and non-Ethernet personalities, firmware file missing/corrupt paths, MSI-X fallback to MSI/INTa, VF exact MSI-X rejection, CMT devices with multiple hwfns, kdump vector reduction, RDMA vector partitioning, LL2 allocation only for personalities that need it, link set/get for legacy and extended-speed capable firmware, media/transceiver matrix capability reporting, NVM flash validation and parser fault injection, MCP response error handling, workqueue cancellation during unload/recovery, periodic doorbell recovery scheduling, and protocol callback nullability.

Useful runtime instrumentation includes dynamic debug for `NETIF_MSG_DRV`, `NETIF_MSG_INTR`, and QED module masks; lockdep around workqueue/tasklet/IRQ stop; DMA API debugging for PCI mappings; firmware-class tests for missing and malformed files; KASAN/KMSAN for NVM parser bounds; and fault injection for `request_firmware()`, `pci_enable_msix_range()`, `qed_ptt_acquire()`, `qed_resc_alloc()`, `qed_hw_init()`, and MCP NVM writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_main.c -->
