# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_noinline.c

## Purpose

Harness for XDP program tests with noinline BPF helper/subprogram structure. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_xdp_noinline` skeleton, `bpf_prog_test_run_opts()` through the selftest helpers, and packet fixtures from `network_helpers.h`.

## Control Flow

The test loads the noinline skeleton and runs packet test cases to ensure XDP behavior remains correct when logic is split into non-inlined BPF subprograms.

## State and Persistence Behavior

Only skeleton state and packet buffers exist during the test.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends on BPF subprogram call support in XDP programs.

## Risks and Edge Cases

Failures can indicate verifier/JIT subprogram issues rather than packet parser logic alone.

## Test Signals

Expected XDP return values and packet/result state from the noinline skeleton test run.
