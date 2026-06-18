# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_perf.c

## Purpose

Small dispatcher for XDP performance-oriented selftests. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_progs.h` selftest entry point and the paired XDP performance BPF object invoked by the harness.

## Control Flow

The function delegates to the selftest framework for the XDP performance case; local control flow is intentionally minimal.

## State and Persistence Behavior

No local persistent state.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

Because this is a thin wrapper, all substantive behavior is in the paired BPF object and framework registration.

## Test Signals

Pass/fail is the selftest framework result for the XDP performance subtest.
