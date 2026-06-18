<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_btf.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_btf.c

Purpose: regression test for map BTF lifetime when maps/programs are freed asynchronously and map BTF is shared by normal maps or map-in-map inner maps.

Important APIs and functions: `do_test_normal_map_btf()` loads `normal_map_btf`, attaches, triggers by setting PID and sleeping, duplicates the array map fd, creates many percpu array maps to delay deferred frees, destroys the skeleton, syncs RCU, waits, closes helper maps, and finally closes the duplicated array fd. `do_test_map_in_map_btf()` performs the same pattern for `map_in_map_btf`, deleting the inner map from the outer map before destroying.

Control flow: `test_map_btf()` runs `array_btf` and `inner_array_btf` subtests. Both force map BTF references to outlive the BPF program and surrounding skeleton objects.

State and persistence: temporary map fds and duplicated inner/array fds hold BTF references past skeleton destruction. RCU waits and sleeps model deferred cleanup timing.

Dependencies and integration: depends on `normal_map_btf.skel.h`, `map_in_map_btf.skel.h`, `kern_sync_rcu()`, and map fd duplication semantics.

Risks and test signals: absence of use-after-free/crash during delayed close is the key signal, plus `done` BSS confirmation. Timing sleeps are heuristic and may be sensitive to slow or heavily loaded systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_btf.c -->
