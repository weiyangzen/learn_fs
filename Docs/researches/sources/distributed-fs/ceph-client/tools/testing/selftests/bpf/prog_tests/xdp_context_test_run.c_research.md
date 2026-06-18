# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_context_test_run.c

## Purpose

XDP context and metadata test-run suite. It validates `bpf_prog_test_run_opts()` context validation, XDP metadata propagation into TC, TAP/TUN and mirred paths, dynptr access to metadata, and helper behavior that mutates skb headroom. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_prog_test_run_opts()`, `struct xdp_md`, `bpf_tc_hook_create/attach()`, `bpf_xdp_attach()`, `open_tuntap()`, raw AF_PACKET `sendto()`, `tc mirred`, `bpf_prog_stream_read()`, and `test_xdp_context_test_run`/`test_xdp_meta` skeletons.

## Control Flow

`test_xdp_context_test_run()` runs valid and invalid context layouts, checking errno and normalized output context. `test_xdp_context_veth()` builds TX/RX namespaces with veth, attaches XDP and TC, sends a marker packet, and checks BSS. `test_xdp_context_tuntap()` runs TAP subtests for data_meta, dynptr read/write/slice/offset, cloned metadata survival, and helpers that adjust VLAN/head/tail/proto.

## State and Persistence Behavior

Transient namespaces, veth/TAP/dummy interfaces, TC hooks, XDP attachments, skeleton BSS `test_pass`, and stderr streams. Cleanup frees namespaces and skeletons.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires tuntap, clsact/mirred, TC, XDP generic attach, and dynptr/helper support.

## Risks and Edge Cases

Many subtests depend on network privileges and kernel helper semantics. Invalid context tests rely on precise errno (`EINVAL`, `E2BIG`). Diagnostic output comes from BPF program stderr streams.

## Test Signals

Signals include expected context rejection cases, normalized valid context/data sizes, `test_pass` from veth/TAP/mirred paths, and readable stderr on failure.
