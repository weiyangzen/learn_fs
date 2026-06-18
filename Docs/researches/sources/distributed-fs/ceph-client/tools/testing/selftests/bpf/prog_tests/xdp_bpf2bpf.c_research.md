# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_bpf2bpf.c

## Purpose

Selftest for XDP BPF-to-BPF calls and perf-event metadata reporting across packet sizes. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_xdp`/`test_xdp_bpf2bpf` skeletons, `perf_buffer`, `bpf_prog_test_run_opts()`, a `struct meta` sample callback, and packet buffer sizing around `BUF_SZ`.

## Control Flow

The test opens XDP programs, configures perf-buffer callbacks, runs packet-size cases through an XDP program that calls into other BPF functions, and validates returned metadata/sample state in `test_ctx`.

## State and Persistence Behavior

State is `test_ctx`, perf-buffer samples, packet buffers, and skeleton maps/BSS. No durable state.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends on BPF-to-BPF call support for XDP programs and perf-event delivery.

## Risks and Edge Cases

Perf-buffer polling/ordering can make failures look like missing samples. Packet-size boundaries must match the paired BPF program expectations.

## Test Signals

Expected signals are successful test-run returns, perf sample callback invocation, and metadata fields matching the packet size/action under test.
