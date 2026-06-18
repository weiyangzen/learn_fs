# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xdp_cpumap_attach.c

## Purpose

Selftest for attaching programs to CPUMAP entries, including frags compatibility and negative fd/program-type cases. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`bpf_cpumap_val`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, `bpf_prog_get_info_by_fd()`, `bpf_xdp_attach/detach()`, live-frame `bpf_prog_test_run_opts()`, `kern_sync_rcu()`, and skeletons for normal/frags CPUMAP helpers.

## Control Flow

The normal test creates a namespace, attaches a redirect program to loopback, stores a `BPF_XDP_CPUMAP` program fd in a cpumap entry, verifies stored program id, sends a live-frame packet, waits for flush, checks redirect count, and then tests invalid direct attach, non-CPUMAP program, non-BPF fd, closed fd, and frags/non-frags incompatibility. The frags test performs the inverse compatibility check.

## State and Persistence Behavior

Transient namespace, loopback XDP attachment, cpumap entries, BSS redirect count, and one `/dev/null` fd for negative checks.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires CPUMAP entry program support and XDP live-frame test run.

## Risks and Edge Cases

Map-entry program compatibility rules are strict; mixing frags and non-frags programs must remain rejected. The namespace cleanup path must detach XDP to avoid leakage.

## Test Signals

Program id in map entry must match, redirect count must become nonzero, and invalid map updates/attaches must return `-EINVAL`, `-EBADF`, or nonzero as expected.
