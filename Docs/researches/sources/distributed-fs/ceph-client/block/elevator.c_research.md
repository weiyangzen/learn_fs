# sources/distributed-fs/ceph-client/block/elevator.c

Purpose: implements the block multi-queue elevator core: scheduler registration, scheduler switching, merge hash/rbtree helpers, sysfs `iosched` handling, and default scheduler selection.

Important APIs and functions: exported helpers include `elv_bio_merge_ok()`, `elv_rqhash_del()`, `elv_rqhash_add()`, `elv_rqhash_reposition()`, `elv_rb_add()`, `elv_rb_del()`, `elv_rb_find()`, `elv_register()`, `elv_unregister()`, `elv_rb_former_request()`, and `elv_rb_latter_request()`. Internal control routines include `elevator_find_get()`, `elevator_alloc()`, `elevator_exit()`, `elv_merge()`, `elv_attempt_insert_merge()`, `elv_merged_request()`, `elv_merge_requests()`, `elevator_switch()`, `elevator_change()`, `elevator_change_done()`, `elv_update_nr_hw_queues()`, `elevator_set_default()`, `elevator_set_none()`, `elv_iosched_store()`, and `elv_iosched_show()`.

Control flow: schedulers register `struct elevator_type` instances in a global list, optionally with an io-context slab cache. Merge paths first try queue `last_merge`, then the elevator hash for back/discard merges, then scheduler-specific `request_merge()`. Scheduler switching loads modules before freezing, allocates scheduler resources, freezes and cancels work, exits the old scheduler under `elevator_lock`, initializes the new scheduler or `none`, unfreezes, unregisters old sysfs/debugfs state, and registers new sysfs/debugfs state. Default setup picks `mq-deadline` for single queue or shared-tags devices unless disabled.

State and persistence: global scheduler state is `elv_list`. Per-queue state is `struct elevator_queue`, including type, scheduler tags/data, sysfs kobject, flags, lock, and merge hash. State persists while the queue uses the scheduler and is replaced on switch.

Dependencies and integration points: depends on blk-mq scheduler resource allocation, queue freeze/quiesce, request merging helpers from `blk.h`, blk-cgroup IO contexts, runtime PM headers, WBT interactions, sysfs/kobject/debugfs, request-module autoloading, and the `iosched` queue attribute.

Risks and test signals: switching must avoid kernfs/update-nr-hwq deadlocks, resource leaks on failed initialization, stale hash entries, and module refcount mistakes. Test scheduler register/unregister, duplicate names, sysfs switching to valid/invalid schedulers and `none`, module autoload, switching during disk removal, hardware queue count changes, merge hash correctness after back merges, default `mq-deadline` selection, and debugfs/sysfs teardown ordering.
