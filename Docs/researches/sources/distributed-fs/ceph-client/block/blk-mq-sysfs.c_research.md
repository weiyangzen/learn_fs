# sources/distributed-fs/ceph-client/block/blk-mq-sysfs.c

## Purpose
`blk-mq-sysfs.c` creates and destroys the `/sys/block/<disk>/mq` hierarchy for blk-mq queues. It exposes each hardware context and its CPU children, plus read-only attributes for tag counts and CPU affinity.

## Important APIs, Types, And Functions
Public functions are `blk_mq_hctx_kobj_init()`, `blk_mq_sysfs_init()`, `blk_mq_sysfs_deinit()`, `blk_mq_sysfs_register()`, `blk_mq_sysfs_unregister()`, `blk_mq_sysfs_unregister_hctxs()`, and `blk_mq_sysfs_register_hctxs()`. Release callbacks are `blk_mq_sysfs_release()`, `blk_mq_ctx_sysfs_release()`, and `blk_mq_hw_sysfs_release()`. Hctx attributes are `nr_tags`, `nr_reserved_tags`, and `cpu_list`.

## Control Flow
Initialization creates the queue-level mq kobject and per-CPU context kobjects. Registering a disk adds `mq` under the disk kobject, sends `KOBJ_ADD`, locks `tag_list_lock`, and adds each hctx kobject plus child `cpuN` kobjects. On any registration failure, previously added hctx/context kobjects are removed and a `KOBJ_REMOVE` is sent. Unregistration removes hctx trees under the same tag-list lock and deletes the queue mq kobject. Hctx show operations run under `q->elevator_lock` so tag pointers and hctx state are stable enough for sysfs output.

## State And Persistence
State is kobject lifetime state attached to `blk_mq_ctxs`, `blk_mq_ctx`, and `blk_mq_hw_ctx`. Release callbacks free percpu contexts, hctx cpumasks, context arrays, and hctx objects. The sysfs files expose live runtime values and do not persist configuration.

## Dependencies And Integration Points
The file integrates with sysfs/kobject infrastructure, disk device kobjects, blk-mq hctx/context topology, tag-set locking, CPU masks, and queue registration state.

## Risks And Test Signals
Risks include kobject reference leaks, double deletion during hctx reconfiguration, racing queue registration checks, and PAGE_SIZE formatting truncation in large CPU lists. Tests should cover disk register/unregister, partial hctx registration failure, hctx re-register after hardware queue count changes, CPU-list formatting on large systems, and sysfs reads during elevator switches.
