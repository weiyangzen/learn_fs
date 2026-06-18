<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/local_kptr_stash.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/local_kptr_stash.c

Purpose: validates local kptr stashing, unstashing, and refcount acquisition rules for BPF objects, including negative verifier cases.

Important APIs and functions: each success helper loads `local_kptr_stash`, runs one or more skeleton programs with `bpf_prog_test_run_opts()` over `pkt_v4`, and checks return values. Covered programs include `stash_rb_nodes`, `stash_plain`, `stash_local_with_root`, `unstash_rb_node`, `refcount_acquire_without_unstash`, and `stash_refcounted_node`. `test_local_kptr_stash_fail()` uses `RUN_TESTS(local_kptr_stash_fail)`.

Control flow: `test_local_kptr_stash()` runs named subtests for simple stash, plain stash, local root association, unstash, refcount acquire before/after stashing, and verifier failures.

State and persistence: BPF-side local objects and refcounted nodes live only for the skeleton lifetime. Return values such as `42` and `2` encode expected object availability/refcount states.

Dependencies and integration: depends on `local_kptr_stash.skel.h`, `local_kptr_stash_fail.skel.h`, and packet test-run support.

Risks and test signals: signals are successful program test runs plus expected return values. Risks are verifier semantic changes for local kptr ownership, RB-tree roots, or refcount acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/local_kptr_stash.c -->
