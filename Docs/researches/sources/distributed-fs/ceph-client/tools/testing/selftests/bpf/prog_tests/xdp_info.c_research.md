# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_info.c

## Purpose

Serial XDP info/query test on loopback. It validates `bpf_xdp_query_id()` before and after generic XDP attach and checks that loopback reports no driver-mode feature flags. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_xdp_query_id()`, `bpf_xdp_query()`, `bpf_prog_test_load()` for `xdp_dummy.bpf.o`, `bpf_prog_get_info_by_fd()`, `bpf_xdp_attach()`, `bpf_xdp_detach()`, `bpf_xdp_query_opts`, and loopback ifindex 1.

## Control Flow

The test first confirms no XDP program id is reported for default or SKB mode. It loads `xdp_dummy.bpf.o`, records the program id, attaches it to loopback in SKB mode, verifies default and SKB queries return that id while DRV mode returns zero, then queries feature flags and detaches.

## State and Persistence Behavior

Transient loopback XDP state only; cleanup must detach any program installed by the test.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

Assumes loopback is ifindex 1 and that no unrelated XDP program is attached by the environment.

## Test Signals

Expected query success and expected program id/zero-id values for the tested state.
