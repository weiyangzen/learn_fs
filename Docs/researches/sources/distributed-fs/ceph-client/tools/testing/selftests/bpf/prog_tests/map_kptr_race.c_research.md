<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_kptr_race.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_kptr_race.c

Purpose: regression suite for kptr reference leaks during map destruction races in hash maps, percpu hash maps, and socket local storage maps.

Important APIs and functions: `get_map_id()` retrieves map IDs with `bpf_map_get_info_by_fd()`. `read_refs()` runs `count_ref`. `test_htab_leak()` and `test_percpu_htab_leak()` create a map with kptr references, attach watcher fentry/fexit programs (`map_put`, `htab_map_free`) to observe map free, destroy the original skeleton, sync RCU, wait for `map_freed`, and assert refcount. `test_sk_ls_leak()` uses loopback TCP to trigger socket local storage kptr logic before watching map free.

Control flow: `serial_test_map_kptr_race()` runs hash, percpu hash, and socket local-storage leak subtests serially because they observe global/free timing.

State and persistence: two skeleton instances are used: one creates the race state, one watches map free by target map ID. Fds, sockets, and skeletons are closed after each subtest.

Dependencies and integration: depends on `map_kptr_race.skel.h`, fentry/fexit attachment, RCU sync, network helpers, and map IDs.

Risks and test signals: `map_freed == 1` and `read_refs() == 2` prove no leaked extra reference. Risks include timing/poll loops, missing fentry targets, and race behavior differing by kernel implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_kptr_race.c -->
