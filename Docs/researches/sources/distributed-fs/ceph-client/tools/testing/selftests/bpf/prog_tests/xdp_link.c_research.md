# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_link.c

## Purpose

Serial regression test for coexistence rules between legacy netlink-style XDP program attachment and BPF link-based XDP attachment on loopback. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`test_xdp_link` skeletons, `bpf_prog_get_info_by_fd()`, `bpf_xdp_attach()`, `bpf_xdp_detach()`, `bpf_xdp_query_id()`, `bpf_program__attach_xdp()`, `bpf_link_update()`, `bpf_link_get_info_by_fd()`, `bpf_link__fd()`, and loopback ifindex 1.

## Control Flow

The test loads two skeleton instances and obtains program ids. It attaches the first program through `bpf_xdp_attach()`, proves a BPF link cannot replace that legacy attachment, detaches it, attaches via BPF link, proves legacy attach/update cannot replace the active link, then exercises valid and invalid `bpf_link_update()` replacement using expected old program fds before checking link info and cleanup semantics.

## State and Persistence Behavior

State is the active loopback XDP program, one BPF link owned by `skel1`, and temporary legacy attach options. Destroying the skeleton/link should remove the attachment.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces.

## Risks and Edge Cases

Loopback state conflicts can cause false failures. Link lifetime semantics are the core behavior under test, so premature fd/link close changes outcomes.

## Test Signals

Expected attach/query results while the link is live and automatic detach/cleanup after link destruction.
