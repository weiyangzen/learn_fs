<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.c_research.md`.

Purpose: implements per-CPT kfabric endpoints, immediate receive buffer lifecycle, send/tagged/RMA post operations, replay queues for `-EAGAIN`, endpoint allocation/free, and memory-region key allocation.

Important APIs/types/functions: immediate receive helpers `kfilnd_ep_post_recv()`, `kfilnd_ep_imm_buffer_put()`, `kfilnd_ep_post_imm_buffers()`, `kfilnd_ep_cancel_imm_buffers()`; operation posters `kfilnd_ep_post_send()`, `kfilnd_ep_post_tagged_send()`, `kfilnd_ep_post_tagged_recv()`, `kfilnd_ep_post_read()`, `kfilnd_ep_post_write()`, `kfilnd_ep_cancel_tagged_recv()`; replay helpers `kfilnd_ep_queue_tn_replay()` and `kfilnd_ep_flush_replay_queue()`; lifecycle `kfilnd_ep_alloc/free()`; key helpers `kfilnd_ep_get_key()` and `kfilnd_ep_put_key()`.

Control flow: allocation creates RX/TX CQs, RX/TX contexts, binds them, enables them, allocates physically contiguous multi-receive buffers, initializes replay queues/timer/work, and IDA keys. Immediate buffer put decrements refs and reposts; `-EAGAIN` queues the buffer for timer-driven replay. KFI post helpers validate device state, optionally inject fake errors, submit provider operations, and return `-EAGAIN` for transaction replay. Replay work drains queued transactions and buffers into their original handlers. Free waits for replay count, cancels receives, waits for buffer refs and transaction list to drain, frees buffers, closes contexts/CQs, destroys keys, and frees memory.

State and persistence behavior: endpoint state persists for the NI lifetime: KFI contexts/CQs, receive buffers, transaction list, replay lists, replay timer/work, and IDA key allocator. Immediate buffers carry refcounts and repost suppression. Transaction keys are unique per endpoint up to `KFILND_EP_KEY_MAX`.

Dependencies and integration: depends on kfabric endpoint/tagged/RMA APIs, completion queues, transaction state machine, peer addressing/session key bits, LNet CPT CPU masks, fail-location framework, timers, workqueues, and Linux IDA.

Risks: teardown can wait indefinitely if transactions or RX refs leak. RKEY composition combines session key and endpoint key; ordering with peer deletion is security-sensitive. Physically contiguous receive buffer allocation can fail for large sizes. Operation flag combinations must match CQ processing. Replay list manipulation relies on `replay_count` balancing.

Test signals: endpoint allocation per CPT, receive repost and cancel, `-EAGAIN` replay for send/read/write/tagged recv/buffer repost, fail-location fake errors, key exhaustion/reuse, shutdown with active operations, and provider event flag coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.c -->
