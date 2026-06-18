# sources/distributed-fs/ceph-client/block/blk-ioprio.h

## Purpose
`blk-ioprio.h` is the internal block-layer declaration point for the cgroup I/O priority policy. It lets submit-side code call `blkcg_set_ioprio()` without carrying conditional compilation into every caller.

## Important APIs, Types, And Functions
The only API is `blkcg_set_ioprio(struct bio *bio)`. When `CONFIG_BLK_CGROUP_IOPRIO` is enabled, the function is provided by `blk-ioprio.c`; otherwise this header provides a static inline no-op. The header forward-declares `struct request_queue` and `struct bio`, although only `struct bio` is required by the visible function.

## Control Flow
There is no runtime control flow when the feature is disabled; calls compile away. When enabled, callers link to the policy implementation and bio priority may be rewritten according to the bio's cgroup.

## State And Persistence
The header owns no state. It controls build-time behavior only through the Kconfig guard.

## Dependencies And Integration Points
It depends on `linux/kconfig.h` for configuration predicates and integrates with the block submission path by providing a stable function name regardless of feature availability.

## Risks And Test Signals
The main risk is accidental divergence between enabled and disabled builds. Build tests should cover both `CONFIG_BLK_CGROUP_IOPRIO=y` and `n`, and submit-path tests should verify that disabled builds have no priority side effects.
