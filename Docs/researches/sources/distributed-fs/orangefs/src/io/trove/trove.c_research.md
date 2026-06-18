## sources/distributed-fs/orangefs/src/io/trove/trove.c

Purpose: Implements the public Trove storage API wrappers that select the proper backend method for a collection and forward bstream, keyval, dataspace, and collection-info operations.

Important APIs and functions: Bstream wrappers cover read/write at offsets, resize, validate, list I/O, and flush. Keyval wrappers cover read/write/remove, validate, iteration, list operations, flush, and handle-info retrieval. Dataspace wrappers cover create/list-create, remove/list-remove, iterate handles, verify, getattr/list-getattr, setattr, cancel, test/testsome/testcontext. Collection wrappers cover extended attributes, getinfo/setinfo, and filesystem configuration. Global tunables include `TROVE_shm_key_hint` and `TROVE_max_concurrent_io`.

Control flow: Almost every function calls `global_trove_method_callback(coll_id)`, indexes the corresponding method table, and forwards arguments. Keyval read/write/list/remove-list validate that non-binary keys have at least two bytes and are NUL-terminated. `trove_dspace_getattr_list` is one of the few wrappers that rejects a negative method ID. `trove_collection_setinfo` intercepts `TROVE_MAX_CONCURRENT_IO` locally; other options go to the backend management table.

State and persistence: This file stores process-global performance counter pointers and tunables. Persistent storage behavior belongs to backend implementations. Operation state is represented by backend-created `TROVE_op_id` values and tested through dataspace test functions.

Dependencies and integration points: Dispatches through method tables declared in `trove-mgmt.c` and contracts in `trove-internal.h`. Public callers include PVFS server code and flow protocols; DBPF implements the default storage behavior.

Risks: Most wrappers trust the method callback result and table pointers without bounds/null checks. Several validation paths dereference `key_p` or arrays before checking for null. `trove_dspace_remove_list` accepts `hints` publicly but calls an internal vtable member without hints. `trove_collection_setinfo` passes `method_id` as the first backend argument by design, but this unusual ordering is easy to break. Errors in backend asynchronous operations are reported later through test state, so wrapper return values alone are not enough.

Test signals: For each wrapper, test invalid method callback values, null arguments where API promises errors, binary versus string key validation, list-count validation, immediate versus deferred operation completion, hint propagation, max-concurrent-IO setinfo behavior, and backend state returned through `trove_dspace_test*`.
