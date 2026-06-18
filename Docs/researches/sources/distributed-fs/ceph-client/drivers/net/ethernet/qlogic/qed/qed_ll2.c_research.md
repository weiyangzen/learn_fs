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
