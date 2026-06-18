# sources/distributed-fs/ceph-client/block/blk-mq-debugfs.h

## Purpose
`blk-mq-debugfs.h` declares the internal blk-mq debugfs interface and compiles it out cleanly when `CONFIG_BLK_DEBUG_FS` is disabled. It also provides the zoned write-plug debugfs hook with a fallback no-op.

## Important APIs, Types, And Functions
When debugfs is enabled, it defines `struct blk_mq_debugfs_attr` with name, mode, show/write callbacks, and optional seq operations. It declares request renderers and registration/unregistration functions for queues, hctxs, schedulers, scheduler hctxs, and rq-qos. When disabled, all registration functions are static inline no-ops. `queue_zone_wplugs_show()` is declared only when both zoned block devices and block debugfs are enabled.

## Control Flow
The header has no runtime logic beyond disabled-build no-ops. Its compile-time branches keep callers simple and ensure debugfs-dependent code is eliminated from non-debug builds.

## State And Persistence
No state is owned in the header. It defines the shape of transient debugfs state managed by `blk-mq-debugfs.c`.

## Dependencies And Integration Points
It depends on `seq_file`, `request_queue`, `request`, and `blk_mq_hw_ctx` declarations in enabled builds. It is included by blk-mq scheduling, debugfs, and registration code.

## Risks And Test Signals
Risks are prototype drift and build failures in disabled configurations. Build coverage should include `CONFIG_BLK_DEBUG_FS=n`, zoned without debugfs, debugfs without zoned, and full debugfs/zoned enabled builds.
