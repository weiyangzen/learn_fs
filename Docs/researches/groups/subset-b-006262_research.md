# Research Report: subset-b-006262

This grouped report covers the RDS core and InfiniBand/RDMA transport files listed for work item `subset-b-006262`. Each section preserves the source path and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_rdma.c -->
# sources/distributed-fs/ceph-client/net/rds/ib_rdma.c

## Purpose
`ib_rdma.c` implements RDS/IB device address tracking and the transport-specific memory-region (MR) backend used by generic RDS RDMA operations. It maps local IPv4 addresses to `struct rds_ib_device`, moves connections between the global nodev list and per-device connection lists, and manages pooled fast-registration MRs plus on-demand paging (ODP) MRs. The file is the bridge between `rdma.c` socket-level MR objects and low-level IB verbs helpers in `ib_mr.h`.

## Important APIs, Types, and Functions
Key external entry points are `rds_ib_get_device()`, `rds_ib_update_ipaddr()`, `rds_ib_add_conn()`, `rds_ib_remove_conn()`, `rds_ib_destroy_nodev_conns()`, `rds_ib_get_mr()`, `rds_ib_free_mr()`, `rds_ib_sync_mr()`, `rds_ib_flush_mrs()`, `rds_ib_get_lkey()`, `rds_ib_create_mr_pool()`, `rds_ib_destroy_mr_pool()`, `rds_ib_mr_init()`, and `rds_ib_mr_exit()`. The main state carriers are `struct rds_ib_device`, `struct rds_ib_mr`, and `struct rds_ib_mr_pool`, with clean, free, and drop MR lists implemented as lockless `llist_head`s. `rds_ib_odp_mr_worker()` is the deferred deregistration path for ODP MRs.

## Control Flow
IP address lookup walks `rds_ib_devices` under RCU and increments the device refcount on a match. `rds_ib_update_ipaddr()` either adds a new address to the current device or removes it from the old device before adding it to the new one. Connection attach/detach moves `ic->ib_node` between `ib_nodev_conns` and `rds_ibdev->conn_list` under the relevant spinlocks, updating `ic->rds_ibdev` and device references.

MR allocation enters through `rds_ib_get_mr()`. For ODP modes, the function checks device capability, calls `ib_reg_user_mr()`, stores the returned `ib_mr`, advertises/prefetches it, and returns a heap-allocated `rds_ib_mr`. For normal fast-registration, it validates the connection/QP and calls `rds_ib_reg_frmr()` against the 8K or 1M pools. MR freeing places reusable FRMRs on pool lists, tracks pinned-page pressure, queues delayed pool flushes, and optionally performs immediate invalidation if the caller requested it.

MR pool flushing is serialized by `pool->flush_lock`. It drains `drop_list`, `free_list`, and optionally `clean_list` into a temporary list, calls `rds_ib_unreg_frmr()` to unmap/free enough entries, returns reusable entries to `clean_list`, updates `free_pinned`, `dirty_count`, and `item_count`, and wakes waiters. `rds_ib_try_reuse_ibmr()` first attempts clean reuse, then reserves `item_count`, and finally triggers a flush if the pool limit is reached.

## State and Persistence
All state is kernel memory only. Device address and connection lists persist for the life of the IB device/connection. MR pools persist per `rds_ib_device` and are bounded by sysctl/device-derived limits. Pinned pages are accounted through pool counters and page references; ODP MRs are not pinned the same way and are deregistered asynchronously on the MR workqueue. The MR flush workqueue `rds_ib_mr_wq` is module-lifetime state.

## Dependencies and Integration Points
This file depends on RCU list traversal, spinlocks, delayed work, InfiniBand DMA/MR verbs, and helpers declared in `ib.h` and `ib_mr.h`. Generic `rdma.c` calls the transport callbacks exposed here via `struct rds_transport`: `get_mr`, `sync_mr`, `free_mr`, and `flush_mrs`. `rds_ib_get_mr_info()` feeds RDS info snapshots. `rds_ib_dev_put()` and global device lists are provided by the broader IB transport.

## Risks
MR lifetime is refcount- and list-sensitive: a missed `rds_ib_dev_put()`, stale list node, or incorrect `free_pinned` update can leak device references or pinned memory. The code marks all torn-down pages dirty because it does not distinguish read-only and writable MRs, which is conservative but expensive. `rds_ib_get_mr()` returns ODP MRs without setting the `device` pointer in the shown path, so call sites must only use fields valid for ODP. Pool flushing has subtle lockless-list batching and wait behavior; regressions can cause depletion, use-after-free, or stalls.

## Test Signals
Useful tests include MR allocation/free under 8K and 1M pool pressure, repeated `RDS_RDMA_USE_ONCE` and invalidate workloads, device removal with live nodev connections, ODP capable and non-ODP devices, and sysctl limit stress. Runtime signals include `s_ib_rdma_mr_*_reused`, `*_pool_flush`, `*_pool_wait`, `*_pool_depleted`, and warnings from pool destroy checks for nonzero `item_count` or `free_pinned`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_recv.c -->
# sources/distributed-fs/ceph-client/net/rds/ib_recv.c

## Purpose
`ib_recv.c` implements the RDS/IB receive side: receive work request initialization, fragment/incoming allocation and recycling, receive-ring refill, ACK and credit generation, incoming fragment reassembly, congestion bitmap reception, CQE handling, and receive-side slab lifecycle. It converts IB receive completions into `rds_incoming` objects delivered to the generic RDS receive queue.

## Important APIs, Types, and Functions
Exported/internal integration points include `rds_ib_recv_init_ring()`, `rds_ib_recv_alloc_caches()`, `rds_ib_recv_free_caches()`, `rds_ib_inc_free()`, `rds_ib_recv_clear_ring()`, `rds_ib_recv_refill()`, `rds_ib_inc_copy_to_user()`, `rds_ib_recv_init_ack()`, `rds_ib_set_ack()`, `rds_ib_attempt_ack()`, `rds_ib_ack_send_complete()`, `rds_ib_piggyb_ack()`, `rds_ib_recv_cqe_handler()`, `rds_ib_recv_path()`, `rds_ib_recv_init()`, and `rds_ib_recv_exit()`. Main private types are `struct rds_ib_incoming`, `struct rds_page_frag`, `struct rds_ib_recv_work`, `struct rds_ib_refill_cache`, and `struct rds_ib_ack_state`.

## Control Flow
Ring initialization prebuilds each `ib_recv_wr` with two SGEs: one DMA-mapped RDS header buffer and one later-filled page fragment. Refill obtains exclusive refill ownership through `RDS_RECV_REFILL`, allocates a receive slot from `i_recv_ring`, ensures an incoming object and fragment exist, DMA maps the fragment for device writes, posts the WR, and advertises newly posted credits if flow control is active. If allocation fails, the ring allocation is undone and receive work is requeued when the ring is low or empty.

Allocation is optimized through per-CPU refill caches. Freed incoming objects and fragments are first accumulated in per-CPU linked lists, batched through a lockless transfer pointer, and later moved into `ready` lists for refill reuse. The global `rds_ib_allocation` limit caps incoming-object allocation and is initialized to roughly 30 percent of RAM in `rds_ib_recv_init()`.

Receive CQE handling uses `rds_ib_ring_oldest()` to match the oldest posted receive, unmaps the fragment DMA mapping, processes successful completions, frees any unconsumed fragment, advances the ring free counter, and triggers refill when the ring is low. `rds_ib_process_recv()` validates minimum size and header checksum, processes ACK and credit fields present in every frame, recognizes ACK-only frames, starts or continues single-message reassembly on `ic->i_ibinc`, checks fragment header consistency, and on message completion either applies a congestion bitmap or calls `rds_recv_incoming()`.

ACK control maintains one special ACK WR outside normal ring accounting. `rds_ib_set_ack()` records the next sequence to acknowledge and optionally sets `IB_ACK_REQUESTED`. `rds_ib_attempt_ack()` sends an ACK-only frame if one is requested, no ACK is already in flight, and a send credit is available. `rds_ib_piggyb_ack()` clears the request and returns the ack sequence for data-header piggybacking.

## State and Persistence
Per-connection receive state includes `i_recv_ring`, `i_recvs`, `i_ibinc`, `i_recv_data_rem`, ACK fields, and refill caches. Per-module state includes two slab caches and the allocation counter. Receive fragments hold page references until consumed and recycled. Incoming messages retain references until socket delivery is complete.

## Dependencies and Integration Points
The file depends on `ib_post_recv()`, DMA mapping helpers, RDS ring utilities, generic message checksum helpers, `rds_recv_incoming()`, congestion map APIs, and send-credit helpers in `ib_send.c`. Its `inc_copy_to_user` and `inc_free` callbacks are installed in the IB transport. It also consumes sysctl state from `ib_sysctl.c` and page fragment allocation from `page.c`.

## Risks
Receive reassembly assumes one fragmented message at a time per connection; header mismatch or lost fragments force reconnect. ACK-only frame handling must recycle the fragment correctly because it bypasses normal incoming ownership. Cache list manipulation is unusual and list-head misuse can corrupt caches. Ring refill races are controlled by a bit flag and waitqueue wakeups; incorrect unalloc/free ordering can make posted WR accounting lie. Flow-control ACKs can deadlock if credit withholding and advertisement logic regresses.

## Test Signals
Stress tests should cover fragmented messages, zero-length ACK-only frames, checksum failures, receive-ring depletion, memory allocation limit hits, congestion bitmap frames, flow-control credit return, and reconnect during partial reassembly. Counters `s_ib_rx_cq_event`, `s_ib_rx_ring_empty`, `s_ib_rx_refill_from_cq`, `s_ib_rx_refill_from_thread`, `s_ib_rx_alloc_limit`, `s_ib_ack_sent`, `s_ib_ack_send_failure`, and `s_ib_ack_send_delayed` are important runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_recv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_ring.c -->
# sources/distributed-fs/ceph-client/net/rds/ib_ring.c

## Purpose
`ib_ring.c` provides the small ring-accounting primitive used by RDS/IB send and receive work request arrays. It tracks which WR slots are allocated by the producer and freed by completion handlers without embedding transport-specific state.

## Important APIs, Types, and Functions
The file operates on `struct rds_ib_work_ring` from `ib.h`. Public functions are `rds_ib_ring_init()`, `rds_ib_ring_resize()`, `rds_ib_ring_alloc()`, `rds_ib_ring_free()`, `rds_ib_ring_unalloc()`, `rds_ib_ring_empty()`, `rds_ib_ring_low()`, `rds_ib_ring_oldest()`, and `rds_ib_ring_completed()`. It also declares `rds_ib_ring_empty_wait`, used when shutdown or completion logic waits for all signaled sends/ring entries to drain.

## Control Flow
`rds_ib_ring_init()` zeroes the ring and sets capacity. Allocation computes `avail = w_nr - used`, returns the smaller of requested and available entries, stores the starting position, advances `w_alloc_ptr`, and increments `w_alloc_ctr`. Completion/free advances `w_free_ptr`, atomically adds to `w_free_ctr`, and wakes waiters when the ring becomes empty. `rds_ib_ring_unalloc()` rolls back producer-side allocation when later setup or credit acquisition fails. `rds_ib_ring_completed()` converts a completed WR id and oldest index into the number of contiguous entries completed.

## State and Persistence
Ring state is in-memory per connection: allocation pointer/counter and free pointer/counter. Counters are intentionally wraparound-friendly; used entries are derived from the difference between producer and atomic free counters. The capacity can be resized only before the QP is live and only when the ring is empty.

## Dependencies and Integration Points
Send and receive paths use the same primitive. The model assumes allocations are serialized by the caller, while frees happen from completion context and can race only with allocation. This contract is documented in the file and is required by `ib_send.c` and `ib_recv.c`.

## Risks
`rds_ib_ring_unalloc()` subtracts an unsigned value and relies on modulo arithmetic; callers must not unallocate more than they just allocated. `rds_ib_ring_completed()` assumes ordered completions and contiguous accounting; out-of-order completion behavior would break this model. `BUG_ON(diff > ring->w_nr)` catches accounting corruption but also means a bug can panic the kernel.

## Test Signals
Unit-style validation can exercise wraparound allocation/free, partial allocation, rollback, resize-before-use, oldest/completed math across the end of the ring, and empty/low thresholds. Integration signals include send/receive ring full counters and empty-ring warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_send.c -->
# sources/distributed-fs/ceph-client/net/rds/ib_send.c

## Purpose
`ib_send.c` implements RDS/IB transmit work: normal SEND frames, RDMA READ/WRITE work requests, masked atomic operations, send completion handling, DMA unmapping, message completion notification, flow-control credit accounting, piggybacked ACK handling, and send-ring initialization/cleanup.

## Important APIs, Types, and Functions
Core functions include `rds_ib_xmit()`, `rds_ib_xmit_rdma()`, `rds_ib_xmit_atomic()`, `rds_ib_send_cqe_handler()`, `rds_ib_send_grab_credits()`, `rds_ib_send_add_credits()`, `rds_ib_advertise_credits()`, `rds_ib_send_init_ring()`, `rds_ib_send_clear_ring()`, and `rds_ib_xmit_path_complete()`. Important helpers are `rds_ib_send_unmap_op()`, `rds_ib_send_unmap_data()`, `rds_ib_send_unmap_rdma()`, `rds_ib_send_unmap_atomic()`, and `rds_ib_set_wr_signal_state()`.

## Control Flow
`rds_ib_xmit()` is called by generic send code with the connection send path serialized. It allocates enough send-ring slots for RDS_FRAG_SIZE fragmentation, optionally acquires flow-control credits, maps the data scatterlist on first use, finalizes header flags and extension headers, piggybacks any pending ACK, attaches credit advertisement if needed, builds a linked list of `ib_send_wr`s, marks selected WRs signaled, hands the message reference to the final fragment, and posts the chain with `ib_post_send()`. Partial progress is represented through `op_dmasg` and `op_dmaoff`.

`rds_ib_xmit_rdma()` maps the RDMA op SG list unless an ODP MR is supplied, allocates enough ring entries to send the entire RDMA operation, chunks SGEs according to device `max_sge`, chooses READ or WRITE opcodes, optionally uses the ODP lkey/address, and posts a WR chain. It does not support partial RDMA progress. `rds_ib_xmit_atomic()` builds a single masked atomic fetch-add or compare-swap WR, maps the 8-byte return buffer for DMA_FROM_DEVICE, and posts it.

Completion handling first separates the special ACK WR id from normal ring entries. Normal completions calculate contiguous completed entries, unmap data/RDMA/atomic resources by opcode, translate IB completion status into RDS RDMA status, wake message waiters when the final op unmapped, drop message references, free ring entries, update signaled count, requeue send work when space/credits become available, and drop the connection on unexpected errors while up.

Flow control stores send credits and posted receive credits in one atomic integer. `rds_ib_send_grab_credits()` uses `cmpxchg` to atomically reserve send credits and drain posted-credit advertisements, withholding the last credit unless it can carry a credit update. `rds_ib_send_add_credits()` receives peer credits and requeues send work. `rds_ib_advertise_credits()` accumulates locally posted receive buffers and requests an ACK when enough credits should be advertised.

## State and Persistence
Per-connection send state includes `i_send_ring`, `i_sends`, `i_data_op`, header DMA buffers, `i_signaled_sends`, `i_unsignaled_wrs`, and `i_credits`. Per-message state tracks mapped SGs, active RDMA/atomic operations, final operation, flags, extension headers, and refcounts. State is volatile kernel memory; progress survives transient send-loop exits through message and connection fields, not persistent storage.

## Dependencies and Integration Points
The file depends on IB verbs, the RDS ring helper, generic message extension/checksum helpers, `rdma.c` completion callbacks, ACK helpers in `ib_recv.c`, transport state from `ib.h`, and sysctls in `ib_sysctl.c`. It is the primary implementation behind `struct rds_transport` callbacks `xmit`, `xmit_rdma`, `xmit_atomic`, and `xmit_path_complete`.

## Risks
The send path has many rollback paths. Failed `ib_post_send()` must undo ring allocation, signaled counters, and partial final-op ownership correctly. Flow-control atomic packing is subtle and can deadlock both peers if the last-credit rule is broken. Completion relies on ordered contiguous CQEs for ring freeing. DMA mapping/unmapping direction must match op type; mistakes can corrupt payloads or completion buffers. RDMA and atomic error completion semantics are user-visible through notifier queues.

## Test Signals
Exercise normal sends across fragmentation boundaries, zero-length sends, flow-control throttling, credit advertisement piggybacking, ACK WR completion, RDMA read/write with multi-SGE and ODP cases, atomic FADD/CSWP, send-ring full rollback, CQ error statuses, and reconnect during outstanding sends. Useful counters include `s_ib_tx_cq_event`, `s_ib_tx_ring_full`, `s_ib_tx_throttle`, `s_ib_tx_sg_mapping_failure`, `s_ib_tx_credit_updates`, `s_ib_tx_stalled`, `s_send_rdma_bytes`, and `s_recv_rdma_bytes`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_send.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_stats.c -->
# sources/distributed-fs/ceph-client/net/rds/ib_stats.c

## Purpose
`ib_stats.c` defines and exports the per-CPU RDS/IB statistics block and provides the RDS info callback that aggregates IB transport counters for user-space inspection.

## Important APIs, Types, and Functions
The file defines `DEFINE_PER_CPU_SHARED_ALIGNED(struct rds_ib_statistics, rds_ib_stats)`, the string table `rds_ib_stat_names[]`, and `rds_ib_stats_info_copy()`. The names correspond by order to the fields of `struct rds_ib_statistics` in `ib.h`.

## Control Flow
`rds_ib_stats_info_copy()` returns the number of available stats. If the caller-provided capacity is large enough, it iterates over online CPUs, treats each per-CPU statistics struct as a `uint64_t` array, sums every field into a local aggregate, and passes values and names to `rds_stats_info_copy()`.

## State and Persistence
Counters are per-CPU volatile kernel counters reset at module load. They persist while the module remains loaded and are not written to disk. Alignment reduces false sharing on hot paths.

## Dependencies and Integration Points
The file integrates with the generic RDS info mechanism (`rds_info_iterator`) and generic stats formatting (`rds_stats_info_copy()`). Transport hot paths update the counters through `rds_ib_stats_inc()` and `rds_ib_stats_add()` macros declared in `ib.h`.

## Risks
The string table and `struct rds_ib_statistics` must remain in exact order and count alignment. A field added to the struct without a corresponding name silently produces confusing user-visible output. The current name table omits the final cache add/remove fields visible in the struct, so maintainers should verify intended ABI/count behavior before extending it.

## Test Signals
Validate that info queries report the expected element count, that counters increase under send/receive/RDMA workloads, and that table-size changes remain compatible with RDS info consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_sysctl.c -->
# sources/distributed-fs/ceph-client/net/rds/ib_sysctl.c

## Purpose
`ib_sysctl.c` registers runtime tunables for the RDS/IB transport under `net/rds/ib`. These tunables bound send and receive WR counts, the maximum unsignaled WR batch size, the receive allocation cap, and a legacy flow-control knob.

## Important APIs, Types, and Functions
Global tunables are `rds_ib_sysctl_max_send_wr`, `rds_ib_sysctl_max_recv_wr`, `rds_ib_sysctl_max_recv_allocation`, `rds_ib_sysctl_max_unsig_wrs`, and `rds_ib_sysctl_flow_control`. Lifecycle functions are `rds_ib_sysctl_init()` and `rds_ib_sysctl_exit()`. The registration state is held in `rds_ib_sysctl_hdr`.

## Control Flow
Initialization registers `rds_ib_sysctl_table` with `register_net_sysctl(&init_net, "net/rds/ib", ...)`. Exit unregisters the table if present. Min/max handlers constrain WR counts to at least 1 and unsignaled WRs to 1..64. `flow_control` is exposed but documented as functionally inert due to protocol compatibility with RDS 3.0 initial credit negotiation.

## State and Persistence
Sysctl values are mutable runtime kernel state scoped to the initial network namespace registration in this file. They are not persisted by the module itself; system sysctl configuration may restore them externally. Receive initialization may adjust `rds_ib_sysctl_max_recv_allocation` based on system RAM.

## Dependencies and Integration Points
`ib_send.c` reads `rds_ib_sysctl_max_unsig_wrs` for signaled completion batching. Connection setup uses max send/receive WR values through wider IB setup code. `ib_recv.c` uses `rds_ib_sysctl_max_recv_allocation` to cap incoming allocations.

## Risks
Oversized WR limits can make QP/CQ creation fail later at hardware boundaries. Too-large receive allocation allows significant pinned/page memory pressure; too-small values cause receive starvation. The `flow_control` knob appears writable but does not enable the documented behavior, so operational tooling should not rely on it.

## Test Signals
Validate sysctl registration/unregistration, min/max enforcement, connection setup with small and large WR limits, receive allocation limit behavior, and unsignaled WR completion cadence under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/ib_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/info.c -->
# sources/distributed-fs/ceph-client/net/rds/info.c

## Purpose
`info.c` implements the RDS getsockopt information snapshot framework. It lets RDS subsystems register fixed-record info providers and copies their snapshots into user buffers through pinned user pages.

## Important APIs, Types, and Functions
The local `struct rds_info_iterator` tracks pinned pages, current mapped address, and page offset. Public functions are `rds_info_register_func()`, `rds_info_deregister_func()`, `rds_info_iter_unmap()`, `rds_info_copy()`, and `rds_info_getsockopt()`. Registered provider callbacks use `struct rds_info_lengths` to report record count and size.

## Control Flow
Providers register by option number in `rds_info_funcs[]` under `rds_info_lock`. `rds_info_getsockopt()` reads the user-supplied buffer length, validates wrapping and negative lengths, pins the user pages if length is nonzero, looks up the provider, initializes an iterator at the user's page offset, calls the provider, unmaps any active kmap, compares required total bytes with supplied length, writes the required length back to `optlen`, and returns either element size or `-ENOSPC`.

`rds_info_copy()` is the provider-side copy helper. It keeps an atomic kmap active across consecutive copies to avoid repeated mapping overhead, copies across page boundaries, and advances the iterator.

## State and Persistence
The only persistent state is the registered callback table. Pinned pages and kmap state are request-local and released before return. No data is stored on disk or retained after the query beyond provider registration.

## Dependencies and Integration Points
Transport and core RDS modules register callbacks for stats, connections, messages, and RDMA state. The copy mechanism depends on `pin_user_pages_fast()`, `kmap_atomic()`, and fixed-size snapshot contracts. `info.h` exposes the provider API.

## Risks
Providers must set `lens->each` and `lens->nr` correctly; `BUG_ON(lens.each == 0)` turns provider bugs into kernel failures. The framework pins the full user buffer before invoking providers; very large lengths can create memory pressure, though length validation prevents overflow. Providers must call `rds_info_iter_unmap()` before sleeping if they perform blocking work while using the iterator.

## Test Signals
Test zero-length size probes, too-small buffers returning `-ENOSPC` and updated length, invalid option numbers, callback register/deregister ordering, page-boundary copies, and providers that produce snapshots larger than one page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/info.h -->
# sources/distributed-fs/ceph-client/net/rds/info.h

## Purpose
`info.h` declares the RDS information snapshot framework used by `info.c` and provider modules. It defines the callback ABI and copy helpers for fixed-record getsockopt information sources.

## Important APIs, Types, and Functions
`struct rds_info_lengths` carries provider output shape: number of records and bytes per record. `struct rds_info_iterator` is opaque to providers except through helper functions. `rds_info_func` is the provider callback type. The header declares registration, deregistration, getsockopt dispatch, iterator copy, and iterator unmap functions.

## Control Flow
The intended control flow is: a subsystem registers an `rds_info_func` for an RDS info option; user space calls the RDS getsockopt; `info.c` pins/maps the destination; the provider fills `lens` and optionally copies fixed records using `rds_info_copy()`; the dispatcher returns the total required length and element size.

## State and Persistence
The header itself owns no state. It documents that providers must make the snapshot shape visible through `lens` and only copy when the caller's provided length can fit the snapshot.

## Dependencies and Integration Points
Included by `rds.h`, so the info API is visible throughout the RDS core and transports. It depends on kernel socket types and user pointer conventions supplied by including translation units.

## Risks
The callback contract is simple but strict. If providers copy more than `len`, report inconsistent `lens`, or sleep with an active iterator mapping, user-visible info calls can fail or trigger kernel bugs.

## Test Signals
Provider tests should verify record counts, `len` gating, and correct use of `rds_info_copy()`/`rds_info_iter_unmap()` across short and multi-page buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/loop.c -->
# sources/distributed-fs/ceph-client/net/rds/loop.c

## Purpose
`loop.c` implements the in-kernel RDS loopback transport used when source and destination resolve to the same host. It bypasses wire transport and feeds an outgoing `rds_message` directly into the generic receive path.

## Important APIs, Types, and Functions
The file defines `struct rds_loop_connection`, global `rds_loop_transport`, and lifecycle functions `rds_loop_net_init()`, `rds_loop_net_exit()`, and `rds_loop_exit()`. Transport callbacks include `rds_loop_xmit()`, `rds_loop_inc_free()`, `rds_loop_recv_path()`, `rds_loop_conn_alloc()`, `rds_loop_conn_free()`, `rds_loop_conn_path_connect()`, and `rds_loop_conn_path_shutdown()`.

## Control Flow
Connection allocation stores a small loopback-private object in `conn->c_transport_data` and links it onto the global `loop_conns` list under `loop_conns_lock`. Connect completion simply calls `rds_connect_complete()`. Transmit validates that no partial-fragment state is passed, initializes the embedded `rm->m_inc` incoming object, takes an extra message reference so the embedded incoming remains valid, calls `rds_recv_incoming()` with local/foreign address roles adjusted for loopback, drops acked send state with the message sequence, and releases the incoming. Congestion bitmaps are not sent to loopback; they directly mark the peer map uncongested.

Module exit sets an unloading flag, waits for RCU readers, moves all loopback connections to a temporary list, and destroys them outside the spinlock. Per-net namespace exit filters loopback connections by `c_net` and destroys matching entries.

## State and Persistence
The global `loop_conns` list tracks active loopback connections. `rds_loop_unloading` is an atomic module-lifetime flag consulted by `t_unloading`. No state persists beyond module/net namespace lifetime. Message lifetime is managed by pairing the extra loopback addref with `rds_loop_inc_free()`.

## Dependencies and Integration Points
Loopback integrates with the generic transport table through `struct rds_transport`. It reuses `rds_message_inc_copy_to_user()` for delivery and generic connection/send/receive helpers for state transitions. `rds_single_path.h` maps legacy single-path fields to `c_path[0]`.

## Risks
Because the incoming object is embedded in the outgoing message, refcount pairing is critical. Address role inversion must remain correct or sockets will see wrong source/destination metadata. Exit destroys connections and assumes passive loopback connections are not present. Loopback intentionally omits RDMA transmit callbacks, so code paths must avoid selecting it for RDMA offload.

## Test Signals
Test local send/recv delivery, source address/port reporting, congestion bitmap short-circuiting, socket close while loopback incoming is queued, namespace teardown, and module unload with active loopback connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/loop.h -->
# sources/distributed-fs/ceph-client/net/rds/loop.h

## Purpose
`loop.h` declares the loopback transport object and lifecycle functions used by the RDS core during module and network-namespace setup/teardown.

## Important APIs, Types, and Functions
The header exports `rds_loop_transport`, `rds_loop_net_init()`, `rds_loop_net_exit()`, and `rds_loop_exit()`. It does not define transport internals; those remain private to `loop.c`.

## Control Flow
Core initialization can register per-net operations with `rds_loop_net_init()`, use `rds_loop_transport` when loopback is preferred, and call `rds_loop_exit()`/`rds_loop_net_exit()` during teardown.

## State and Persistence
No state is stored in the header. State lives in `loop.c` globals and per-connection private allocations.

## Dependencies and Integration Points
Consumers include RDS initialization/transport selection code. The declared transport has type `RDS_TRANS_LOOP` and uses the generic `struct rds_transport` shape from `rds.h`.

## Risks
The header is intentionally minimal; the main risk is lifecycle ordering. Calls to `rds_loop_exit()` should occur after new loopback connection creation has stopped.

## Test Signals
Build coverage should ensure declarations match definitions. Runtime coverage should validate loopback transport registration and namespace cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/loop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/message.c -->
# sources/distributed-fs/ceph-client/net/rds/message.c

## Purpose
`message.c` implements allocation, reference counting, payload storage, extension header manipulation, zero-copy completion bookkeeping, user-copy helpers, and flush waiting for `struct rds_message`. It is the shared message object layer used by loopback, TCP, and IB transports.

## Important APIs, Types, and Functions
Public functions include `rds_message_alloc()`, `rds_message_alloc_sgs()`, `rds_message_map_pages()`, `rds_message_copy_from_user()`, `rds_message_inc_copy_to_user()`, `rds_message_addref()`, `rds_message_put()`, `rds_message_populate_header()`, `rds_message_add_extension()`, `rds_message_next_extension()`, `rds_message_add_rdma_dest_extension()`, `rds_message_wait()`, `rds_message_unmapped()`, and `rds_notify_msg_zcopy_purge()`. Zero-copy helpers manage `struct rds_msg_zcopy_info`, `struct rds_znotifier`, and socket zcookie queues.

## Control Flow
Messages are allocated with extra inline space for all scatterlist entries needed by data, RDMA, and atomic ops. `rds_message_alloc_sgs()` partitions that inline SG pool. Payload creation either copies user data into pages allocated by `rds_page_remainder_alloc()` or, for zero-copy, pins user pages with `iov_iter_get_pages2()` and records a notifier for completion cookies. `rds_message_map_pages()` builds a message over kernel page addresses and marks `RDS_MSG_PAGEVEC` so purge will not free those pages.

Header helpers initialize fixed fields, pack extension headers into the 16-byte extension area, and iterate extension headers by implied type length. RDMA destination cookies use the generic extension packing helper.

`rds_message_put()` drops a refcount and on final put verifies the message is off socket/connection lists, purges payload pages, zero-copy notifiers, RDMA/atomic operation state, and referenced MRs, then frees the message. Zero-copy completion records cookies into per-socket batches, wakes socket waiters, and handles early failure before a message is attached to a socket. `rds_message_wait()` blocks until the transport clears `RDS_MSG_MAPPED` via `rds_message_unmapped()`.

## State and Persistence
Message state persists while refcounted by socket queues, connection queues, transport work requests, or embedded incoming delivery. Payload pages are owned by the message except for pagevec messages and zero-copy pinned user pages. Zero-copy cookie state is persisted in the socket zcookie queue until collected by receive-side control messages.

## Dependencies and Integration Points
The file depends on `page.c` for small page-fragment allocation, `rdma.c` for RDMA/atomic cleanup, socket wakeups, Linux iterator/page pinning APIs, and checksum/extension constants from `rds.h`. Transports call addref/put and `rds_message_unmapped()` around DMA ownership. Receive code uses `rds_message_inc_copy_to_user()` for loopback messages.

## Risks
SG pool accounting must match all control-message extra-size calculations; otherwise later SG allocation fails or overwrites memory. Zero-copy paths must unaccount pinned pages on every error path. Extension header space is tiny and silently refuses additions by returning 0, so callers must handle dropped metadata. Final purge must not free pagevec pages. Refcount/list assertions can BUG on lifetime violations.

## Test Signals
Test copied and zero-copy sends, partial user-copy failures, SG pool exhaustion, extension packing/iteration near the 16-byte limit, message flush waiting, pagevec messages, and RDMA/atomic cleanup on final put. Check zcopy completion control messages and memory pin accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/message.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/page.c -->
# sources/distributed-fs/ceph-client/net/rds/page.c

## Purpose
`page.c` provides a small page-fragment allocator for RDS scatterlists. It reduces memory waste for sub-page payload fragments by caching the unused remainder of one page per CPU.

## Important APIs, Types, and Functions
The local `struct rds_page_remainder` stores a cached page, current offset, and `local_lock_t`. Public APIs are `rds_page_remainder_alloc()` and `rds_page_exit()`.

## Control Flow
For full-page-or-larger requests, `rds_page_remainder_alloc()` allocates a page directly and returns it as a full-page SG entry. For smaller requests, it disables bottom halves, locks the per-CPU remainder, discards an existing page if the remaining space is too small, returns a fragment from the cached page when possible, increments the page reference for the caller, advances the offset aligned to 8 bytes, and frees the cached holder reference when the page is exhausted. If no cached page exists, it temporarily drops the local lock and BH disable, allocates a highmem page, then installs it if another caller did not race to fill the slot.

`rds_page_exit()` walks all possible CPUs and frees any cached remainder page.

## State and Persistence
State is per-CPU volatile cache state. Each cached page is retained by the allocator until exhausted, discarded, or module exit. Returned SG fragments hold their own page references and are freed by message or receive cleanup.

## Dependencies and Integration Points
`message.c` uses this for copied user payloads. `ib_recv.c` uses it for receive fragments. Statistics `s_page_remainder_hit` and `s_page_remainder_miss` provide runtime insight.

## Risks
The allocator assumes transmit users treat page regions as read-only while devices own them. Incorrect caller freeing or missing page puts can leak highmem pages. Local locking/BH behavior must remain valid for callers from softirq-adjacent paths. Tiny unusable remainders are intentionally discarded, which affects memory efficiency but simplifies fragmentation.

## Test Signals
Exercise small allocations across CPUs, alignment behavior, exact page exhaustion, direct full-page allocation, allocation failure propagation, and `rds_page_exit()` freeing cached pages. Monitor hit/miss counters and page refcount leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/rdma.c -->
# sources/distributed-fs/ceph-client/net/rds/rdma.c

## Purpose
`rdma.c` implements generic RDS RDMA and atomic socket-control behavior above any specific transport. It manages user MR registration/freeing, socket MR lookup trees, use-once invalidation, RDMA/atomic send operation construction from control messages, page pinning, ODP fallback setup, and operation cleanup.

## Important APIs, Types, and Functions
Public functions include `rds_get_mr()`, `rds_get_mr_for_dest()`, `rds_free_mr()`, `rds_rdma_drop_keys()`, `rds_rdma_unuse()`, `rds_rdma_extra_size()`, `rds_cmsg_rdma_args()`, `rds_cmsg_rdma_dest()`, `rds_cmsg_rdma_map()`, `rds_cmsg_atomic()`, `rds_rdma_free_op()`, `rds_atomic_free_op()`, and `__rds_put_mr_final()`. Key helpers are `rds_pages_in_vec()`, `rds_mr_tree_walk()`, `rds_destroy_mr()`, `rds_pin_pages()`, `__rds_rdma_map()`, and `rds_rdma_pages()`.

## Control Flow
MR registration validates that the socket is bound and has a transport with `get_mr`, checks address/length overflow, requires `can_do_mlock()`, calculates page count, limits MR size to the 1 MiB RDS message bound plus alignment, allocates an `rds_mr`, pins pages with `pin_user_pages_fast(FOLL_LONGTERM|FOLL_WRITE)`, builds an SG table, and calls the transport `get_mr` callback. If long-term pinning is unsupported, it requests ODP registration instead. On success it stores the transport-private MR, builds the 64-bit cookie from rkey and offset, optionally copies the cookie to user space, inserts the MR into the socket RB tree, and returns with refcounts balanced.

MR freeing handles a zero-cookie flush-all special case, otherwise removes the keyed MR from the RB tree under `rs_rdma_lock`, applies invalidate if requested, and drops the reference. `rds_rdma_drop_keys()` removes all socket MRs during socket teardown and flushes transport MRs. `rds_rdma_unuse()` reacts to incoming RDMA extension headers by syncing the MR and freeing use-once or forced MRs.

`rds_cmsg_rdma_args()` parses sendmsg RDMA control messages, validates vector count, preallocates notifier state, calculates and pins local pages, supports a single-vector ODP fallback by registering a local ODP MR, fills SG entries, checks local byte count against remote vector capacity, and marks the RDMA op active. `rds_cmsg_rdma_dest()` attaches an existing local MR cookie for delivery to the remote and syncs it for device reads. `rds_cmsg_rdma_map()` registers a new MR and embeds its cookie into the outgoing message. `rds_cmsg_atomic()` parses masked/nonmasked FADD and CSWP requests, validates 8-byte alignment, pins the local result page, and fills the atomic op.

## State and Persistence
Socket MR state is in `rs->rs_rdma_keys`, an RB tree keyed by rkey. Each `rds_mr` is kref-managed, holds transport-private state, flags for use-once/invalidate/write, and a back pointer to the owning socket. RDMA and atomic send ops live inside `struct rds_message` until completion or message purge. Pinned user pages persist until op or MR cleanup; ODP MRs avoid explicit page arrays.

## Dependencies and Integration Points
Transport callbacks in `struct rds_transport` provide actual MR registration, sync, free, and flush behavior. `ib_rdma.c` is the IB implementation. `message.c` allocates SG space and calls cleanup. `recv.c` processes RDMA extension headers and invokes `rds_rdma_unuse()`. User ABI structs come from `<linux/rds.h>`.

## Risks
Long-term page pinning has security/resource implications and depends on `can_do_mlock()`. Error paths must release partially pinned pages and SG arrays exactly once. RB-tree lookup/insertion assumes rkeys are unique; duplicate behavior is guarded by BUG assumptions. ODP fallback changes cleanup ownership and only supports a single local vector in this code. Atomic control messages require strict 8-byte alignment and correct result buffer dirtying. User-controlled vector lengths need overflow checks throughout.

## Test Signals
Test MR get/free/drop, duplicate/invalid cookies, zero-cookie flush, use-once RDMA unuse, invalidation, RDMA read/write vectors with unaligned addresses, ODP supported and unsupported paths, mlock permission failures, atomic variants, notifier generation, and socket teardown with outstanding MRs. Watch for leaked pins, RB tree corruption, and RDMA status control messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/rdma_transport.c -->
# sources/distributed-fs/ceph-client/net/rds/rdma_transport.c

## Purpose
`rdma_transport.c` is the module entry point and RDMA CM event dispatcher for the RDS RDMA/IB transport. It initializes IB transport support, creates IPv4 and IPv6 RDMA listeners, dispatches CM events to transport callbacks, and tears down listeners on module exit.

## Important APIs, Types, and Functions
The file defines `rds_rdma_cm_event_handler()`, `rds6_rdma_cm_event_handler()`, `rds_rdma_listen_init_common()`, `rds_rdma_listen_init()`, `rds_rdma_listen_stop()`, module `rds_rdma_init()`, and module `rds_rdma_exit()`. Listener state is in `rds_rdma_listen_id` and, when IPv6 is enabled, `rds6_rdma_listen_id`.

## Control Flow
The common CM handler resolves the transport from the RDMA device node type, locks `conn->c_cm_lock` when a connection context exists, bails out safely if disconnecting, and switches on CM event type. Connect requests call `cm_handle_connect`; address resolution sets service type/min RNR timer and resolves route; route resolution verifies the cm_id still belongs to the connection, sets service level from TOS, and calls `cm_initiate_connect`; established events call `cm_connect_complete`; reject/error/disconnect/timewait events generally drop the connection.

Listener setup creates an RDMA CM id in `init_net` with `RDMA_PS_TCP` and `IB_QPT_RC`, binds to the supplied sockaddr, and listens with backlog 128. IPv4 listens on `RDS_PORT` for compatibility. IPv6, when compiled, listens on `RDS_CM_PORT` and logs but tolerates failure. Module init calls `rds_ib_init()` first, then starts listeners; failure after IB init unwinds with `rds_ib_exit()`. Exit stops listeners before shutting down IB.

## State and Persistence
Listener CM ids are module-lifetime global state. Per-connection CM progress lives in `struct rds_connection` and transport-private IB connection state. No persistent storage is used.

## Dependencies and Integration Points
This file depends on RDMA CM APIs, IB transport callbacks in `rds_ib_transport`, and connection management helpers from RDS core. It includes `rds_single_path.h` because connection state macros expect single-path compatibility in some CM paths.

## Risks
The local `trans` variable is assigned only for `RDMA_NODE_IB_CA`; unexpected node types would leave it undefined before use. CM event handling must avoid destroying cm_ids while shutdown is in progress, hence the lock and disconnecting checks. Rejection compatibility logic resets proposed protocol version only in specific cases. Listener bind behavior may associate ids with devices, limiting failover as noted by the comment.

## Test Signals
Cover module load/unload, IPv4 and IPv6 listener creation, connect request handling, address/route/established event sequences, rejection with legacy incompat data, device removal, disconnect/timewait events, and route resolution races where a cm_id no longer matches connection private state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/rdma_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/rdma_transport.h -->
# sources/distributed-fs/ceph-client/net/rds/rdma_transport.h

## Purpose
`rdma_transport.h` declares the RDMA CM listener constants and module-level interfaces shared by `rdma_transport.c` and the IB transport implementation.

## Important APIs, Types, and Functions
It defines `RDS_CM_PORT`, `RDS_RDMA_RESOLVE_TIMEOUT_MS`, and `RDS_RDMA_REJ_INCOMPAT`. It declares `rds_rdma_cm_event_handler()`, `rds6_rdma_cm_event_handler()`, external `rds_ib_transport`, and `rds_ib_init()`/`rds_ib_exit()`.

## Control Flow
The header supports the flow where module init brings up IB transport support, installs RDMA CM listeners using the handlers declared here, and dispatches CM events back into IB connection-management callbacks.

## State and Persistence
No state is owned by this header. Constants influence listener port selection, route resolution timeout, and legacy rejection handling.

## Dependencies and Integration Points
The header includes RDMA verbs/CM headers and `rds.h`. It is included by `rdma_transport.c` and `ib.h`, binding the generic RDMA CM module to the IB transport object.

## Risks
Port constants are compatibility-sensitive: `RDS_PORT` remains in `rds.h` for legacy IPv4 while `RDS_CM_PORT` is used for IPv6/RDMA CM. Changing these values breaks wire compatibility. Reject reason encoding is explicitly legacy and should not be expanded casually.

## Test Signals
Build tests should validate IPv6 conditional handler declarations. Integration tests should confirm listener ports and route resolve timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/rdma_transport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/rds.h -->
# sources/distributed-fs/ceph-client/net/rds/rds.h

## Purpose
`rds.h` is the central private header for the RDS kernel implementation. It defines wire constants, core connection/socket/message/RDMA/statistics structures, transport callback contracts, inline helpers, and cross-file prototypes for the RDS core and transports.

## Important APIs, Types, and Functions
Major definitions include protocol constants (`RDS_PROTOCOL_*`, `RDS_PORT`), fragmentation and message limits (`RDS_FRAG_SIZE`, `RDS_MAX_MSG_SIZE`), congestion map sizing, connection states, connection flags, multipath constants, `struct rds_conn_path`, `struct rds_connection`, `struct rds_header`, extension header structs, `struct rds_incoming`, `struct rds_mr`, `struct rds_message`, `struct rds_notifier`, `struct rds_transport`, `struct rds_sock`, and `struct rds_statistics`.

Important inline helpers include RDMA cookie pack/unpack, `rds_message_zcopy_queue_init()`, socket/container conversions, send/receive buffer accounting, connection state tests/transitions, checksum make/verify, and `rds_destroy_pending()`. The header declares APIs implemented by bind, congestion, connection, message, page, recv, send, rdma, stats, sysctl, threads, and transport modules.

## Control Flow
The header shapes the entire RDS control flow. Sockets bind to `rds_sock` state, sends allocate `rds_message` objects, transports implement `struct rds_transport` callbacks for connection setup, transmit, RDMA, receive-copy, MR management, and stats, and received transport fragments eventually become `rds_incoming` objects queued on sockets. Connection paths carry per-path send queues, retransmit lists, state, work items, sequence counters, and transport-private data. Multipath-aware transports can use multiple `rds_conn_path` entries; `rds_single_path.h` maps older single-path code to path zero.

## State and Persistence
All structures are in-kernel volatile state. `rds_connection` persists per address pair, `rds_conn_path` persists per path, `rds_sock` persists per socket, `rds_message` and `rds_incoming` are refcounted per operation, and `rds_mr` persists while registered to a socket. No state is persisted to disk by this header.

## Dependencies and Integration Points
The header includes core networking, scatterlist, highmem, RDMA CM, mutex, rhashtable, refcount, IPv6, and `info.h`. It is included by almost every RDS source file and by transport-specific files. Its `struct rds_transport` is the primary integration contract between RDS core and loopback/TCP/IB transports.

## Risks
This header is ABI-adjacent for internal modules and wire-format-critical for `struct rds_header` and extension constants. Layout or semantic changes can break transport interoperability, user control-message behavior, or refcount ownership. The transport callback contract is broad; missing callback validation in callers can produce NULL dereferences. Many inline state helpers warn when used with multipath-capable transports incorrectly.

## Test Signals
Useful validation includes build coverage across IPv4/IPv6 and RDMA configs, protocol header checksum/extension packing tests, transport callback conformance tests, connection state transition stress, multipath handshake tests, socket receive/send queue lifetime tests, and RDMA MR lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/rds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/rds_single_path.h -->
# sources/distributed-fs/ceph-client/net/rds/rds_single_path.h

## Purpose
`rds_single_path.h` provides compatibility macros that map legacy single-path `struct rds_connection` field names to `conn->c_path[0]` members. It lets older transport code operate on path zero without rewriting every field access.

## Important APIs, Types, and Functions
The header defines macros such as `c_xmit_rm`, `c_xmit_sg`, `c_xmit_hdr_off`, `c_lock`, `c_next_tx_seq`, `c_send_queue`, `c_retrans`, `c_next_rx_seq`, `c_transport_data`, `c_state`, `c_flags`, `c_send_w`, `c_recv_w`, `c_cm_lock`, `c_waitq`, `c_unacked_packets`, and `c_unacked_bytes`.

## Control Flow
Files that include this header access `conn->c_*` names while actually reading or writing `conn->c_path[0].cp_*`. This supports single-path transports and CM logic that are not multipath-aware.

## State and Persistence
The header owns no state; it aliases existing path-zero state in `struct rds_connection`.

## Dependencies and Integration Points
Included by loopback, IB send/receive, RDMA transport, and other single-path-oriented files. It depends on `rds.h` structure layout.

## Risks
These macros hide whether code is path-aware. Including the header in multipath-capable logic can accidentally force all operations onto path zero. Macro aliases also make code search and refactoring harder because field access is not explicit.

## Test Signals
Build coverage should catch layout mismatches. Multipath tests should ensure files using this header are either truly single-path or intentionally operate on path zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/rds_single_path.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/recv.c -->
# sources/distributed-fs/ceph-client/net/rds/recv.c

## Purpose
`recv.c` implements generic RDS incoming-message handling and socket `recvmsg()`. It initializes/refcounts incoming messages, enforces receive sequence behavior, processes handshake and RDMA extension headers, queues messages on bound sockets, maintains receive-buffer congestion state, returns payload and control messages to user space, drains notification queues, and formats incoming-message info snapshots.

## Important APIs, Types, and Functions
Public functions include `rds_inc_init()`, `rds_inc_path_init()`, `rds_inc_put()`, `rds_recv_incoming()`, `rds_recvmsg()`, `rds_clear_recv_queue()`, `rds_notify_queue_get()`, `rds_inc_info_copy()`, and `rds6_inc_info_copy()`. Important helpers include `rds_recv_rcvbuf_delta()`, `rds_conn_peer_gen_update()`, `rds_recv_incoming_exthdrs()`, `rds_recv_hs_exthdrs()`, `rds_start_mprds()`, `rds_next_incoming()`, `rds_still_queued()`, `rds_notify_cong()`, `rds_cmsg_recv()`, and `rds_recvmsg_zcookie()`.

## Control Flow
Transports call `rds_recv_incoming()` with a completed `rds_incoming`. The function selects the path, drops old retransmitted sequence numbers, advances `cp_next_rx_seq`, handles ping/probe handshake messages, processes multipath and generation-number extension headers, finds the bound destination socket, processes RDMA extension headers, and queues the incoming on `rs_recv_queue` under `rs_recv_lock` if the socket is alive. Queueing updates receive-buffer byte accounting, congestion bits, optional receive timestamp, latency trace, and wakes socket sleepers.

`rds_recvmsg()` first drains RDMA/status notifications or congestion notifications as control messages. If no data is available it either returns `-EAGAIN` in nonblocking mode, optionally after reaping zero-copy completion cookies, or waits on the socket sleep queue. For data, it copies through the transport `inc_copy_to_user` callback, verifies the incoming is still queued, optionally drops it unless `MSG_PEEK` is set, marks `MSG_TRUNC` when user buffer is too small, emits RDMA destination/timestamp/latency control messages, emits zero-copy completion cookies, fills IPv4 or IPv6 source address output, and releases the incoming reference.

Notification handling moves queued `rds_notifier` objects to a temporary list to avoid sleeping while holding `rs_lock`, copies as many as fit in the control buffer, and requeues unconsumed notifications on error. `rds_clear_recv_queue()` is used during socket teardown after unbinding and drops queued incoming objects while reversing receive-buffer accounting.

## State and Persistence
Incoming objects are refcounted and live in transport-private storage or embedded messages. Socket state includes `rs_recv_queue`, `rs_rcv_bytes`, `rs_congested`, `rs_notify_queue`, congestion notification bits, and zero-copy cookie queue. Connection paths persist `cp_next_rx_seq` and handshake/multipath state. All state is volatile kernel memory.

## Dependencies and Integration Points
The file depends on transport callbacks for incoming copy/free, bind lookup via `rds_find_bound()`, send-side ping/pong and retransmit drop helpers, congestion map APIs, RDMA MR unuse from `rdma.c`, message extension parsing from `message.c`, and socket timestamp/errqueue behavior from the networking core.

## Risks
Sequence handling assumes fragments of a message are complete before transport delivery; old retransmitted messages are dropped, but missing middle fragments are hard to detect at this layer. Queue races with another reader are handled by `rds_still_queued()` and iterator revert, but copy-before-drop means careful MSG_PEEK behavior is required. Congestion state hysteresis must match socket byte accounting or peers can be over-throttled. Handshake extension parsing mutates multipath state and can start new connection paths synchronously. Control-message copy failures can leave notifications queued for retry.

## Test Signals
Test receive delivery, no-socket/dead-socket drops, old retransmit sequence drops, MSG_PEEK, MSG_TRUNC, blocking/nonblocking timeout behavior, RDMA destination cmsg, timestamp cmsg, latency trace cmsg, zero-copy completion cmsg, congestion notifications, notification queue truncation, socket teardown queue clearing, ping/pong handshake, and multipath fan-out. Key counters include `s_recv_queued`, `s_recv_delivered`, `s_recv_drop_*`, `s_recv_ack_required`, `s_recv_bytes_added_to_socket`, and `s_recv_bytes_removed_from_socket`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/recv.c -->
