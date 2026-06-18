<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_kptr.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_kptr.c

Purpose: validates map-stored kptr reference counting across map types, local-storage kptrs, element deletion/update, deferred map free, and verifier failure cases.

Important APIs and functions: `test_map_kptr_success()` loads `map_kptr`, runs refcount test programs, optionally updates/deletes array, percpu array, hash, percpu hash, malloc-backed hash, LRU hash, and local-storage map elements, and adjusts expected `data->ref`. `kern_sync_rcu_tasks_trace()` runs an auxiliary BPF program to force RCU Tasks Trace grace period. `wait_for_map_release()` polls `count_ref` until `num_of_refs == 2`. `serial_test_map_kptr()` runs `RUN_TESTS(map_kptr_fail)` and success modes around RCU synchronization.

Control flow: failure tests run first. Success-map subtest exercises delete/update paths, waits for deferred release with both RCU variants, then repeats for synchronous delete observation.

State and persistence: kptr reference counts are shared between BPF maps and skeleton data/BSS. Map destruction and element deletion are intentionally used as lifecycle transitions.

Dependencies and integration: depends on `map_kptr.skel.h`, `map_kptr_fail.skel.h`, `rcu_tasks_trace_gp.skel.h`, packet test-run, and RCU sync helpers.

Risks and test signals: retval zero and expected reference counts are signals. Risks include grace-period timing, deferred free behavior, map-type-specific kptr release, and verifier rule changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_kptr.c -->
