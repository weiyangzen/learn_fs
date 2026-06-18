<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.c_research.md`.

Purpose: implements the kfilnd transaction allocator, wire-message packing/unpacking, transaction state machine, timeout/replay handling, LNet finalization, mempool setup, and bulk buffer mapping.

Important APIs/types/functions: global kmem caches and mempools for transactions and immediate message buffers; packing helpers for hello, immediate, and bulk v1/v2 messages; `kfilnd_tn_unpack_msg()` validation; `kfilnd_tn_process_rx_event()`; state handlers for `TN_STATE_IDLE`, `IMM_SEND`, `IMM_RECV`, `WAIT_COMP`, `WAIT_TAG_COMP`, timeout/fail states, and dispatch table; public `kfilnd_tn_event_handler()`, `kfilnd_tn_alloc()`, `kfilnd_tn_alloc_for_hello()`, `kfilnd_tn_free()`, `kfilnd_tn_init()`, `kfilnd_tn_cleanup()`, `kfilnd_tn_get_mempool_stats()`, and `kfilnd_tn_set_buf()`.

Control flow: outbound LNet sends allocate a transaction, optional key, peer ref, and message buffer, then feed an init event. Inbound immediate receive completions validate headers/checksum/NIDs, allocate a target transaction, attach the posted buffer, and feed RX/hello events. The state machine serializes on `tn_lock`, posts KFI operations via endpoint APIs, returns `-EAGAIN` to queue replay, starts/cancels timeout timers for bulk initiators, finalizes LNet messages/replies, releases peers and buffers, records duration stats, and frees the transaction. Bulk initiator flow posts a tagged receive, sends a bulk request, waits for send and tagged completion, and times out/cancels if needed. Target flow parses into LNet, receives `kfilnd_recv()`, posts read/write RMA or a zero-length tagged send, then finalizes.

State and persistence behavior: transactions are live objects on an endpoint list. They carry status/health, state timestamps, deadlines, replay event/status, LNet messages, peer refs, local/remote keys, KFI context, posted immediate buffer refs, mapped SGL/BVEC data, and timeout work/timer. Mempools persist module-wide and reserve elements based on tunables.

Dependencies and integration: depends on endpoint posting/replay/key APIs, peer cache and hello state helpers, device stats, LNet parse/finalize/reply helpers, checksum routines, DMA or LNet RDMA mapping for GPU buffers, Linux mempool/slab/timer/workqueue, and CFS fail locations.

Risks: this is the highest-risk file. RKEY reuse protection depends on key-before-peer lookup and peer deletion ordering. State/event combinations use `LBUG()` on unexpected input. Some comments mark possible leaks around invalid receive paths and cancel failures. Timeout races are handled with WAIT_TIMEOUT states but require exact event ordering. SGL mapping mutates `orig_nents` and must restore it before free. Mixed-endian byte swapping is TODO.

Test signals: exhaustive state-machine tests for immediate, hello, bulk PUT, bulk GET, zero-length target skips, timeouts, cancels, send/tagged/RMA failures, replay `-EAGAIN`, early RX before hello completion, protocol v1/v2 messages, checksum enabled/disabled, GPU and non-GPU DMA mapping, mempool reserve exhaustion, and teardown with active timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_tn.c -->
