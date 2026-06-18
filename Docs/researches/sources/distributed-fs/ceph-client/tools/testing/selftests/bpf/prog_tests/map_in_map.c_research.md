<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_in_map.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_in_map.c

Purpose: tests concurrent access and update semantics for map-in-map structures, including array/hashtable outers, sleepable access, fd insertion/overwrite/delete, and unsupported lookup-and-delete cases.

Important APIs and functions: `thread_ctx` coordinates update and access threads. `update_map_fn()` repeatedly creates new array inner maps and updates the outer map. `access_map_fn()` triggers BPF programs with `SYS_getpgid` while updates race. `test_map_in_map_access()` selects a program/map by name, loads and attaches `access_map_in_map`, and runs the two threads with a barrier. `add_del_fd_htab()`, `overwrite_fd_htab()`, `lookup_delete_fd_htab()`, and `batched_lookup_delete_fd_htab()` exercise fd-valued hash outer-map operations.

Control flow: top-level runs access tests for array/hash and sleepable variants, then update tests for preallocated and non-preallocated hash outer maps.

State and persistence: temporary inner maps are inserted into outer maps and closed after update; kernel map references persist only while stored in the outer. Threads coordinate four iterations and store error bits in `ctx.err`.

Dependencies and integration: depends on `access_map_in_map.skel.h`, `update_map_in_htab.skel.h`, pthread barriers, syscall triggers, and map-in-map kernel support.

Risks and test signals: no thread errors and expected `-ENOTSUPP` for lookup-and-delete on htab-of-maps are signals. Risks are race sensitivity, missed synchronization, and map fd lifetime regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_in_map.c -->
