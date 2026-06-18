# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_dev_bound_only.c

## Purpose

Regression test for device-bound XDP program loading on a non-offload veth device. It distinguishes `BPF_F_XDP_DEV_BOUND_ONLY` from an ifindex-bound program that would be treated as offloaded. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

Raw `bpf_prog_load()` with `prog_ifindex` and `prog_flags`, simple inline BPF instructions, `if_nametoindex()`, namespace/veth setup helpers, and `BPF_F_XDP_DEV_BOUND_ONLY`.

## Control Flow

The test creates a namespace and veth, loads a dummy XDP program bound to the veth with `BPF_F_XDP_DEV_BOUND_ONLY` and expects success, then loads a second ifindex-bound program without the flag and expects `-EINVAL` because veth does not support offload.

## State and Persistence Behavior

Transient namespace, veth, and two program fds. Namespace deletion removes the veth.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends on XDP offload/dev-bound loader semantics.

## Risks and Edge Cases

If device offload classification changes, the expected `-EINVAL` may change. The test is meant to catch a NULL dereference class in offload handling.

## Test Signals

First program fd is nonnegative; second load returns `-EINVAL`.
