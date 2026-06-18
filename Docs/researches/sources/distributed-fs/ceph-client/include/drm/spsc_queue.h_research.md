# sources/distributed-fs/ceph-client/include/drm/spsc_queue.h

Purpose: implements a small lockless single-producer/single-consumer queue used by DRM scheduler-style code.

Important APIs/types/functions: `struct spsc_node` is the embedded link. `struct spsc_queue` stores consumer `head`, atomic `tail` pointer-to-next, and atomic `job_count`. Inline operations are `spsc_queue_init()`, `spsc_queue_peek()`, `spsc_queue_count()`, `spsc_queue_push()`, and `spsc_queue_pop()`.

Control flow: initialization points `tail` at `head`. Producer disables preemption, increments count, atomically swaps `tail` to the new node's `next`, links the previous tail pointer to the node, uses a write barrier, and returns whether the queue was empty. Consumer reads `head`, advances to `next`, and on last-element slow path CASes `tail` back to `head` or waits until a concurrent producer publishes `next`.

State and persistence: queue state is in `head`, `tail`, and `job_count`. It is runtime-only and assumes exactly one producer and one consumer.

Dependencies and integration: depends on atomics, preemption control, and memory barriers. Integrated by DRM scheduler/job queues where SPSC assumptions hold.

Risks and test signals: using multiple producers or consumers breaks correctness. Barriers, last-element slow path, and job count accuracy are critical. Test empty-to-nonempty wake decisions, concurrent push/pop stress, preemption-sensitive producer paths, and count underflow/overflow assertions.
