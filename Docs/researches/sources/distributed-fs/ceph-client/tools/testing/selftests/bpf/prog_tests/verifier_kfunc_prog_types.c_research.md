# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/verifier_kfunc_prog_types.c

## Purpose

Minimal harness for verifier coverage of kfunc availability across BPF program types. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`RUN_TESTS(verifier_kfunc_prog_types)` and the generated skeleton `verifier_kfunc_prog_types.skel.h`.

## Control Flow

The exported test function delegates all load/attach/expectation handling to the common selftest `RUN_TESTS` macro.

## State and Persistence Behavior

No local state; skeleton and verifier expectation state are managed by the selftest framework.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

Coverage depends entirely on annotations in the paired BPF source and kernel kfunc/BTF availability.

## Test Signals

Pass/fail is reported by `RUN_TESTS`, including expected verifier rejections for unsupported kfunc/program-type combinations.
