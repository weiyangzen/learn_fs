# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_attach.c

## Purpose

Tests XDP attach/replace/detach semantics on loopback and validates failure diagnostics for invalid XDP link attachment flags. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_prog_test_load()`, `bpf_prog_get_info_by_fd()`, `bpf_xdp_attach()`, `bpf_xdp_query_id()`, `bpf_xdp_detach()`, `bpf_xdp_attach_opts.old_prog_fd`, perf-buffer error callback, and `test_xdp_attach_fail` skeleton.

## Control Flow

The main attach test loads three XDP programs, attaches the first with replace semantics, verifies program id, attempts invalid replacement, replaces with a valid old fd, checks id again, then verifies invalid detach and valid detach behavior. The failure path captures expected error text from a skeleton/perf event.

## State and Persistence Behavior

State is current XDP program on ifindex 1 and loaded object fds; detach paths clean up loopback attachment.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It assumes ifindex 1 is loopback and XDP generic attach is available.

## Risks and Edge Cases

Failure to detach leaves loopback modified for later tests. Program id checks are sensitive to querying the same attach mode as used for attach.

## Test Signals

Signals include exact program-id transitions, failed replacement with wrong expected fd, failed detach with wrong old fd, successful detach with correct old fd, and expected invalid-link-flag error text.
