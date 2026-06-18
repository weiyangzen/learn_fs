# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_pull_data.c

## Purpose

Tests XDP pull-data behavior across frame sizes and return values, including large pull constants and packet data preservation. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_xdp_pull_data` skeleton, `bpf_prog_test_run_opts()`, frame-size probing in `find_xdp_sizes()`, `run_test()`, and constants `PULL_MAX`, `PULL_PLUS_ONE`, `XDP_PACKET_HEADROOM`.

## Control Flow

The basic test loads the skeleton, discovers acceptable XDP frame sizes, runs cases with different return values and pull sizes, and validates output packet sizes/contents and error behavior for too-large or boundary pulls.

## State and Persistence Behavior

State is skeleton maps/BSS, packet buffers, and computed frame-size limits. No durable state.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends on XDP test-run frame allocation and headroom/tailroom limits.

## Risks and Edge Cases

Boundary constants are large and can expose integer overflow or frame-size assumptions. Architecture/page-size differences may affect computed limits.

## Test Signals

Expected return values, accepted/rejected pull sizes, and preserved packet data/size across run cases.
