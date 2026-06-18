# sources/distributed-fs/ceph-client/block/blk-mq-tag.c

## Purpose
`blk-mq-tag.c` manages blk-mq driver tag allocation using scalable bitmaps. It tracks active shared-tag users, allocates normal and reserved tags, wakes sleepers, iterates busy requests, drains completed requests, allocates/frees tag maps, resizes shared tag maps, and generates queue-wide unique tags.

## Important APIs, Types, And Functions
Allocation APIs include `blk_mq_get_tag()`, `blk_mq_get_tags()`, `blk_mq_put_tag()`, and `blk_mq_put_tags()`. Activity APIs are `__blk_mq_tag_busy()`, `__blk_mq_tag_idle()`, and `blk_mq_tag_wakeup_all()`. Iteration/drain APIs are `blk_mq_all_tag_iter()`, `blk_mq_tagset_busy_iter()`, `blk_mq_tagset_wait_completed_request()`, and `blk_mq_queue_tag_busy_iter()`. Lifecycle APIs are `blk_mq_init_tags()`, `blk_mq_free_tags()`, `blk_mq_tag_resize_shared_tags()`, `blk_mq_tag_update_sched_shared_tags()`, and `blk_mq_unique_tag()`.

## Control Flow
Before allocating driver tags, busy hctxs mark themselves active and update wake batches based on active users. `blk_mq_get_tag()` chooses reserved or normal bitmap, tries a shallow or full bitmap allocation, returns immediately for NOWAIT failure, or sleeps on the appropriate sbitmap wait state. While waiting it runs the hardware queue, retries allocation, remaps ctx/hctx after sleep, and compensates with a wakeup if the destination bitmap changed. Tags are returned to the corresponding normal or reserved bitmap. Busy iteration walks reserved and normal bitmaps, safely resolves `tags->rqs[]` entries with request references, filters by queue/hctx, and releases references after callbacks. Tag freeing releases sbitmap queues immediately and uses SRCU-delayed freeing when request pages exist.

## State And Persistence
Runtime state lives in `struct blk_mq_tags`: normal and reserved sbitmap queues, `active_queues`, `nr_tags`, `nr_reserved_tags`, request pointer arrays, allocated request pages, lock, and SRCU free callback. No persistent state exists.

## Dependencies And Integration Points
The file integrates with blk-mq allocation data, hctx flags/state, queue usage refs, SRCU-protected tag-set arrays, sbitmap queues, scheduler shared tags, request references, kmemleak, and blk-mq queue dispatch.

## Risks And Test Signals
Risks include missed wakeups while sleeping for tags, underflow of `active_queues`, allocating tags on inactive hctxs, request pointer races after bitmap bits are set, shared-tag fairness regressions, reserved tag misuse, and SRCU free lifetime bugs. Tests should cover NOWAIT allocation failure, reserved-tag pools, hctx remap while waiting, shared versus per-hctx tags, busy iteration during completion, queue teardown with in-flight requests, tag resize, and unique-tag uniqueness across hctxs.
