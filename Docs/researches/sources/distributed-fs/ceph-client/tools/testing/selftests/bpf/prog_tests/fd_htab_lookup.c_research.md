# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fd_htab_lookup.c

## Purpose
Stress-tests concurrent lookup and update of an outer hash map containing inner map IDs, validating safe fd lookup while maps are being replaced and freed.

## Important APIs, types, and functions
Uses `fd_htab_lookup.skel.h`, pthreads, `bpf_map_create()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, and `bpf_map_get_fd_by_id()`. `htab_lookup_fn()` repeatedly reads IDs from the outer map, obtains inner FDs, and checks inner value equals key. `htab_update_fn()` repeatedly creates/replaces inner arrays. `setup_htab()` seeds the map.

## Control flow and state
The test loads the skeleton, obtains `outer_map` FD, initializes eight entries, starts eight writer and sixteen reader threads, joins all, and requires every thread return NULL. Runtime state is shared `htab_op_ctx` with fd, loop count from `FD_HTAB_LOOP_NR`, entry count, and stop flag.

## Dependencies and integration points
Depends on map-in-map semantics, map ID lookup, pthreads, generated skeleton map definition, and kernel refcount correctness under concurrency.

## Risks and test signals
Concurrent `stop` flag is not atomic but used only as a coarse test stop. Passing signal is no lookup/update error, no stale invalid inner map errors except tolerated `-ENOENT`, and all threads joining with NULL return.
