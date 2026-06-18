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
