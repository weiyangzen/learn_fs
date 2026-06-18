# sources/distributed-fs/ceph-client/include/net/codel_qdisc.h

Read `sources/distributed-fs/ceph-client/include/net/codel_qdisc.h` completely for this pass (77 lines, 3024 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/codel_qdisc.h_research.md`.

Purpose: provides the qdisc-specific skb control block layout and helpers needed by CoDel users to timestamp packets at enqueue and recover enqueue time at dequeue.

Important APIs/types/functions: `struct codel_skb_cb` stores `enqueue_time` and `mem_usage` inside the qdisc private control block. `get_codel_cb()` validates private qdisc control block size and returns a typed pointer. `codel_get_enqueue_time()` reads the timestamp, and `codel_set_enqueue_time()` stores `codel_get_time()`.

Control flow: a qdisc using the CoDel plugin calls `codel_set_enqueue_time()` when enqueuing an skb. Later, the CoDel callback passed as `codel_skb_time_t` calls `codel_get_enqueue_time()` so `codel_dequeue()` can compute sojourn delay.

State and persistence: timestamp and optional memory usage live in `skb->cb` for the time the skb is queued. This metadata is transient and must not collide with other qdisc private data.

Dependencies and integration points: depends on `net/codel.h`, `net/pkt_sched.h`, qdisc skb control block helpers, and the owning qdisc's enqueue/dequeue code.

Risks: qdiscs must reserve enough private control-block space or `qdisc_cb_private_validate()` will catch misuse. Any other code that overwrites qdisc CB data while the skb is queued will corrupt CoDel delay measurement. Timestamps must be set at the correct enqueue point, after any requeue semantics are considered.

Test signals: enqueue/dequeue unit tests verifying timestamp storage, private CB size validation, sojourn delay calculation through callbacks, and interactions with qdiscs that also track `mem_usage`.
