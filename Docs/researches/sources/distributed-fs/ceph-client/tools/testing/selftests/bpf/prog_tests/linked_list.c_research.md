<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_list.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_list.c

Purpose: exercises kernel verifier and runtime behavior for BPF intrusive linked lists, including `bpf_list_head`, `bpf_list_node`, required `bpf_spin_lock` ownership, nested lists, map/global/kptr storage, and peek coverage through `linked_list_peek`.

Important APIs and functions: `test_linked_list_fail_prog()` opens `linked_list_fail` with a 1 MiB verifier log, autoloads one named bad program, expects load failure, and searches the verifier log for the exact diagnostic. `test_linked_list_success()` runs selected programs from `linked_list.skel.h` with `bpf_prog_test_run_opts()` and `pkt_v4`. `clear_fields()` resets map/global backing memory through `bpf_map__update_elem()`. `init_btf()`, `list_and_rb_node_same_struct()`, and `test_btf()` synthesize BTF with libbpf `btf__add_*()` APIs to validate kernel-side metadata checks.

Control flow: `test_linked_list()` iterates the fail table, runs synthetic BTF subtests, then runs success modes with and without leaving list objects in backing maps. The success helper uses mode branches for simple push/pop, multiple push/pop, list-in-list, and all operations. `test_linked_list_peek()` delegates to `RUN_TESTS(linked_list_peek)`.

State and persistence: state is transient BPF object state plus map/global storage inside the skeleton. The `leave_in_map` dimension intentionally leaves nodes reachable until object teardown to exercise cleanup, while the non-leave path overwrites map values with `0xff`. BTF objects are loaded into the kernel and freed locally after expected success/failure.

Dependencies and integration: depends on libbpf skeletons `linked_list`, `linked_list_fail`, `linked_list_peek`, `test_btf.h`, `linux/btf.h`, and selftest network packet fixtures. It integrates with the selftest harness through `ASSERT_*` and subtest names.

Risks and test signals: high-value signals are exact verifier messages for missing locks, wrong allocation ownership, invalid direct access, bad offsets, cycles in ownership graphs, and mixed list/rb-node/refcount rules. Fragility comes from diagnostics changing, BTF error codes changing, or layout offsets in the BPF-side structs moving without updating expected strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/linked_list.c -->
