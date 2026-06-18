# sources/distributed-fs/ceph-client/block/elevator.h

Purpose: declares the internal elevator/scheduler interfaces used by block multi-queue schedulers and the elevator core.

Important APIs and types: `enum elv_merge` classifies no/front/back/discard merges. `struct elevator_tags` and `struct elevator_resources` carry scheduler tag/data allocations. `struct elv_change_ctx` coordinates scheduler switching. `struct elevator_mq_ops` defines scheduler callbacks for init/exit, hardware-context lifecycle, merging, depth limiting, request prepare/finish, insertion, dispatch, work detection, completion, requeue, rb traversal, and io-context lifecycle. `struct elevator_type` describes a scheduler implementation and module ownership. `struct elevator_queue` stores the active scheduler type, tags/data, sysfs kobject, lock, flags, and merge hash.

Control flow and integration: scheduler modules fill `elevator_type` and call `elv_register()`. The elevator core allocates `elevator_queue`, invokes scheduler ops through block-mq dispatch and merge paths, and exposes per-scheduler sysfs/debugfs attributes. The header also provides module ref helpers, rb helpers, hash declarations, insertion constants, and scheduler debugfs registration declarations.

State and persistence: this header defines runtime objects whose instances live either globally as registered scheduler types or per queue as active scheduler state. It owns no storage itself.

Dependencies and risks: depends on blk-mq, percpu/io-context infrastructure, hash tables, sysfs attributes, modules, and optional debugfs. Callback signature compatibility is critical; missing mandatory ops are rejected by `elv_register()`. Test compile coverage for schedulers, module load/unload, sysfs attributes, merge callbacks, io-context caches, hardware-context hotplug, and disabled debugfs builds.
