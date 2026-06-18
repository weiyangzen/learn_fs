<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_lsm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_lsm.c

Purpose: tests BPF LSM attachment, enforcement, repeated detach/attach, copy-from-user edge handling, and tail-call program-array behavior for LSM programs.

Important APIs/types/functions: `stack_mprotect()`, `exec_cmd()`, `test_lsm()`, `test_lsm_basic()`, `test_lsm_tailcall()`, `lsm__attach()`, `lsm__detach()`, `bpf_program__attach()`, and program-array updates on `jmp_table`.

Control flow: the basic subtest loads `lsm`, attaches all links, verifies a second direct attach of an already linked program fails, forks/execs `true` and checks `bprm_count`, sets monitored pid and attempts executable stack `mprotect()` expecting `EPERM`, triggers `setdomainname` calls with invalid pointers/lengths to exercise copy paths, detaches, resets counters, and repeats. Tailcall subtest loads `lsm_tailcall`, stores two LSM program fds into the same jump-table slot to validate update behavior.

State and persistence: transient child process, stack memory protection attempt, BSS counters and monitored pid. No durable state.

Dependencies and integration: depends on BPF LSM support, generated skeletons, `true` executable, syscall availability, and program-array support. Integrated as `test_test_lsm`.

Risks: LSM stacking/configuration and process privilege can change attach or enforcement behavior. `errno` after `mprotect` is part of the expected signal. Tailcall subtest uses `CHECK_FAIL(!err)` for the first update, meaning it expects that update to fail; that is intentional coverage but easy to misread.

Test signals: validates attach success, duplicate attach rejection, `bprm_count`, `mprotect_count`, `copy_test == 3`, second attach cycle, and jump-table update outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_lsm.c -->
