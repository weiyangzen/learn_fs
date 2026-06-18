# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-dspace.c

## Purpose
`dbpf-dspace.c` implements DBPF dataspace operations for Trove: create, create-list, remove, remove-list, handle iteration, verify, getattr, getattr-list, setattr, cancel, and completion testing. It is the central metadata layer that connects handle allocation, DB persistence, attr caching, keyval cleanup, bstream cleanup, event tracing, and DBPF operation queues.

## Important APIs, types, and functions
The method table `dbpf_dspace_ops` exports all dspace operations. Creation uses `dbpf_dspace_create()`, `dbpf_dspace_create_op_svc()`, `dbpf_dspace_create_list()`, and `dbpf_dspace_create_list_op_svc()`. Removal uses `remove_one_handle()`, `dbpf_dspace_remove_op_svc()`, and `dbpf_dspace_remove_list_op_svc()`. Attribute helpers `dbpf_dspace_attr_get()` and `dbpf_dspace_attr_set()` are also used by bstream code. Completion paths are `dbpf_dspace_test()`, `dbpf_dspace_testsome()`, and `dbpf_dspace_testcontext()`. `PINT_dbpf_dspace_remove_keyval()` is a cursor deletion callback.

## Control flow and state
Most operations resolve the collection, initialize a queued-or-immediate `dbpf_op`, attach operation-specific payload, start events/perf counters, and call `dbpf_queue_or_service()`. Service functions perform DB work and return `DBPF_OP_COMPLETE`/`1` or negative Trove errors. Threaded builds wait on per-context completion queues and condition variables; non-threaded builds poll/service the queued operation directly. `organize_post_op_statistics()` updates metadata read/write counters after completion.

## Persistence and integration
Dspace records are stored in `coll_p->ds_db` keyed by handle with `TROVE_ds_attributes` as the value. Creation allocates handles and writes attributes, moving any stale bytestream file to a stranded-bstreams location before inserting the record. Removal deletes the dspace record, invalidates attr cache, removes open-cache/bstream state, deletes keyval entries through keyval iteration, syncs keyval DB when needed, and frees the handle. Setattr persists attributes and updates the attr cache. Getattr reads from cache first, then DB, then inserts into cache.

## Dependencies
It depends on handle management, DB abstraction, attr cache, keyval iteration, open cache, bstream method tables, sync/coalescing macros, DBPF thread/queue infrastructure, PINT performance counters, PINT events, and global method callbacks.

## Risks and test signals
This file has broad blast radius. `dbpf_dspace_create_list_op_svc()` passes `op_p->u.d_create.type` instead of `op_p->u.d_create_list.type`, which looks like a union-field bug. Error sign conventions vary between `dbpf_db_*()` positive Trove errors and negative returned service errors. Cache fast paths must preserve behavior identical to queued paths. Threaded completion paths assume valid context ids and non-empty completion queues. Tests should cover forced handles, range allocation failure rollback, stale bstream renaming, attr cache hit/miss behavior, getattr-list partial cache hits, remove cleanup of keyvals and bstreams, iterate position semantics, cancel delegation to bstream ops, threaded and non-threaded completion, and sync-on-remove/setattr behavior.
