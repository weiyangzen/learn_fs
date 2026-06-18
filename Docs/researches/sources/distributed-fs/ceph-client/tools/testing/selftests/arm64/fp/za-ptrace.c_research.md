<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-ptrace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-ptrace.c

Purpose: ptrace ABI selftest for SME ZA register set, including VL changes, disabled ZA representation, and ZA data round-trips.

Important APIs and functions: `get_za` dynamically sizes `user_za_header` reads from `NT_ARM_ZA`; `set_za` writes ZA regsets. `ptrace_set_get_vl`, `ptrace_set_no_data`, `ptrace_set_get_data`, `do_child`, and `do_parent` implement the cases.

Control flow: skip if SME unsupported, fork a traced child, wait for its SIGSTOP, iterate VQs from `SVE_VQ_MIN` to `TEST_VQ_MAX`, set each VL via ptrace after comparing prctl-supported VL in parent, and for supported VLs verify disabled ZA header-only writes and full ZA data write/read.

State and persistence: dynamic buffers for ZA payloads; random data seeded by PID. No disk state.

Dependencies and integration: uses `PTRACE_GETREGSET`/`SETREGSET`, `NT_ARM_ZA`, `PR_SME_SET_VL`, sigcontext ZA sizing macros, and kselftest.

Risks: `ksft_test_result(new_za->vl = prctl_vl, ...)` uses assignment instead of comparison, so that subtest can pass incorrectly if `prctl_vl` is nonzero. Coverage is limited to current architectural VQ range plus one.

Test signals: expected tests are three per candidate VQ; data mismatch, read/write failures, and unsupported VL skips are reported via kselftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/za-ptrace.c -->
