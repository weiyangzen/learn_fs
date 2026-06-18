# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_devmap_attach.c

## Purpose

Selftest for DEVMAP entry-attached XDP programs, attach-type verifier checks, frags compatibility, tail-call attach typing, and veth live-frame redirection. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_devmap_val`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `bpf_prog_get_info_by_fd()`, `bpf_program__set_expected_attach_type()`, `bpf_xdp_attach/detach()`, live-frame `bpf_prog_test_run_opts()`, and DEVMAP helper skeletons.

## Control Flow

Normal DEVMAP tests attach a redirect program, insert a `BPF_XDP_DEVMAP` program into a devmap entry, verify id, trigger a packet, reject direct device attach of a DEVMAP program, and reject incompatible program types/frags. Tail-call tests load combinations of expected attach types and assert accept/reject. The veth case attaches redirect and receiver programs to a veth pair and runs a live-frame packet.

## State and Persistence Behavior

Transient namespace, loopback/veth XDP attachments, devmap entries, BPF objects, and program links. Cleanup deletes namespace and detaches programs.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires DEVMAP entry programs, XDP frags support, and veth native mode for the veth subtest.

## Risks and Edge Cases

Program attach type and frags compatibility rules are intentionally strict. Native XDP on veth may be unavailable in constrained environments.

## Test Signals

Stored devmap program id must match, live-frame test run must succeed, invalid attach/map update combinations must fail, and expected attach-type combinations must match verifier outcomes.
