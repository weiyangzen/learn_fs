# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec.c

## Purpose
This is the main xlator implementation for GlusterFS disperse/EC. It initializes EC private state, parses volume options, manages child up/down notifications and self-heal triggering, registers FOP wrappers, protects internal EC xattrs, handles read-mask configuration, exposes statedump data, and publishes the `xlator_api_t`.

## Important APIs, Types, And Functions
Initialization flows through `mem_acct_init()`, `init()`, `ec_prepare_childs()`, `ec_parse_options()`, `ec_method_init()`, read-policy/read-mask assignment, self-heal daemon init, and subvolume-id dictionary construction. Teardown uses `fini()` and `__ec_destroy_private()`. Notification functions are `notify()`, `ec_notify()`, `ec_notify_cbk()`, `ec_up()`, `ec_down()`, and `ec_get_event_from_state()`. FOP wrappers named `ec_gf_*` adapt GlusterFS xlator FOP signatures to internal EC APIs. `ec_dump_private()` emits runtime state and stripe/heal statistics.

## Control Flow
At startup, the translator allocates `ec_t`, pools for FOP/callback/lock objects, child arrays, matrix coding state, inode table, self-heal state, and volume option values. `GF_EVENT_PARENT_UP` starts a ten-second delayed notification timer so initial child notifications can settle. Child up/down events update bitmasks under `ec->lock`; once enough bricks are up and all have notified, the translator propagates `GF_EVENT_CHILD_UP` and may launch root self-heal. If too many bricks are down, it propagates down. Upcalls are filtered: cache invalidation forces attr invalidation, while EC-domain inodelk contention releases eager locks on the affected inode.

The FOP wrapper table is mostly thin: it chooses quorum flags (`EC_MINIMUM_ONE`, `EC_MINIMUM_MIN`, or `EC_MINIMUM_ALL`) and calls the appropriate internal EC function. Xattr wrappers block direct access to `trusted.ec.*` internals except for the explicit heal/read-mask paths. Marker and heal-info getxattrs are intercepted before normal EC dispatch.

## State And Persistence Behavior
`ec_t` holds child topology, fragment/redundancy geometry, node masks, up/down state, option values, pending FOP lists, self-heal queues, matrix cache, pools, read mask, leaf-to-subvolid mapping, and counters. Persistent on-brick state is not written directly here, but this file defines internal xattr names and prevents users from mutating them. `ec->up`, child masks, timers, and self-heal thread state are runtime-only. `__ec_destroy_private()` includes a deliberate sleep after canceling a timer due to callback cancellation race concerns.

## Dependencies And Integration Points
The file integrates with GlusterFS xlator APIs, event APIs, statedump, upcall-utils, option macros, inode table creation, self-heal daemon (`ec-heald`), coding method (`ec-method`), and all internal EC FOP implementations. The final `xlator_api` identifies the translator as `"disperse"` and marks it maintained.

## Risks
Option parsing directly affects data layout: invalid redundancy or too many subvolumes must be rejected before serving I/O. Notification timing is race-prone because timer cancellation cannot guarantee the callback is not already scheduled. Direct xattr filtering must remain complete or users could corrupt EC metadata. Runtime `cpu-extensions` reconfiguration calls a stub method update, so expectations around live generator changes should be conservative.

## Test Signals
Tests should cover initialization with legal and illegal disperse counts, child notification orderings, delayed mount behavior, parent down while FOPs are pending, read-mask parsing and per-inode read-mask setxattr, internal xattr denial for get/set/remove, marker getxattr handling, self-heal launch on brick recovery, and statedump fields after workload.
