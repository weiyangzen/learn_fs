# sources/distributed-fs/ceph-client/kernel/liveupdate/luo_flb.c

## Purpose
`luo_flb.c` implements File-Lifecycle-Bound global data. FLBs let file handlers declare shared global state that should be preserved once when the first dependent file is preserved, referenced by every dependent file, restored on demand in the new kernel, and finished when the last dependent file is finished.

## Important APIs, Types, and Functions
Internal types are `struct luo_flb_header`, `struct luo_flb_global`, and `struct luo_flb_link`. Global state `luo_flb_global` contains incoming/outgoing serialized headers, the global FLB list, and a count capped by `LUO_FLB_MAX`.

Private per-FLB state is accessed through `luo_flb_get_private()`, which lazily initializes locks, list state, and counts in `struct luo_flb_private`. File lifecycle hooks are `luo_flb_file_preserve()`, `luo_flb_file_unpreserve()`, `luo_flb_file_finish()`, and their per-FLB helpers. Registration APIs are `liveupdate_register_flb()`, `liveupdate_unregister_flb()`, `liveupdate_flb_get_incoming()`, and `liveupdate_flb_get_outgoing()`. FDT setup/serialization functions are `luo_flb_setup_outgoing()`, `luo_flb_setup_incoming()`, and `luo_flb_serialize()`.

## Control Flow
`liveupdate_register_flb()` links an FLB to a registered file handler, checks callback presence, prevents duplicate per-handler and global compatible strings, adds the FLB to the global list on first use, and increments user count. Unregister removes links and drops the global entry when no handlers use it.

When a file is preserved, `luo_flb_file_preserve()` iterates the handler's FLB dependencies in registration order. For each dependency, `luo_flb_file_preserve_one()` calls `.preserve()` only when outgoing count is zero, stores returned data/object, takes the owner module reference, and increments count. On failure, already preserved FLBs in that operation are unpreserved in reverse.

Pre-reboot serialization walks all global FLBs and writes entries for those with outgoing count greater than zero: compatible name, opaque data, and reference count. In the new kernel, `luo_flb_retrieve_one()` finds the matching serialized entry, takes the module reference, calls `.retrieve()`, and caches the restored object. `liveupdate_flb_get_incoming()` exposes that cached object on demand. Finish decrements incoming count per dependent file and calls `.finish()` only when it reaches zero.

## State and Persistence Behavior
Persistent FLB state is a KHO-preserved header page plus `struct luo_flb_ser` entries containing compatible string, opaque data, and dependent-file count. Runtime outgoing and incoming private state separately track data, object pointer, reference counts, retrieved/finished flags, and locks. Module references are held while outgoing state is preserved or incoming state remains unfinished.

## Dependencies and Integration Points
It depends on LUO file handler private list fields, `luo_register_rwlock`, KHO preserved allocation, libfdt, module refs, and liveupdate FLB public callback types. File handlers call `liveupdate_register_flb()` to declare global dependencies and can query incoming/outgoing objects with the getter APIs.

## Risks and Test Signals
Lazy private initialization uses acquire/release ordering and a spinlock; races there would corrupt locks/lists. Count underflow or mismatched preserve/unpreserve/finish calls can leak modules or finish too early. `luo_flb_file_finish_one()` retrieves an FLB during finish if no one retrieved it earlier, so `.retrieve()` must be safe late. Serialization has a fixed one-page cap. Tests should cover multiple handlers sharing one FLB, duplicate compatible rejection, rollback on preserve failure, incoming lazy retrieve, finish after zero references, unregister-all while holding write lock, and capacity exhaustion.
