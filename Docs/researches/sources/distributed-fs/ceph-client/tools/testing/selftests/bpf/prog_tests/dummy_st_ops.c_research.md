# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/dummy_st_ops.c

## Purpose
Tests dummy struct_ops program loading/test-run behavior, argument marshaling, fentry attachment to struct_ops programs, sleepable invocation, null rejection, and negative verifier cases.

## Important APIs, types, and functions
Uses `dummy_st_ops_success.skel.h`, `dummy_st_ops_fail.skel.h`, `trace_dummy_st_ops.skel.h`, `bpf_map__attach_struct_ops()`, `bpf_prog_test_run_opts()`, `bpf_program__set_attach_target()`, and `struct bpf_dummy_ops_state`. Subtests cover return value, pointer argument mutation, multiple arguments, sleepable program, and null pointer rejection.

## Control flow and state
Each subtest loads its own skeleton, optionally attaches tracing skeleton to a target BPF program, runs the target through `bpf_prog_test_run_opts()` with explicit context args, checks return values/BSS, and destroys skeletons. `test_dummy_st_ops()` also runs failure skeleton tests. State is local ctx arrays, dummy state structs, trace BSS, and skeleton BSS.

## Dependencies and integration points
Depends on kernel dummy struct_ops test hook, generated success/fail/trace objects, tracing attach support, and prog test-run for struct_ops-like programs.

## Risks and test signals
Kernel support may be absent or attach intentionally unsupported. Passing signals include `-EOPNOTSUPP` for actual struct_ops attach, expected return values, pointer mutation to `0x5a`, fentry observed original value, captured multiple args, sleepable run success, `-EINVAL` for null, and negative skeleton failures.
