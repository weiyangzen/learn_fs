<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netcnt.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netcnt.c

Purpose: tests BPF network byte/packet accounting for a cgroup using the `netcnt` fixture.

Important APIs and functions: the harness creates/joins a cgroup, loads and attaches `netcnt`, generates network traffic with helpers, reads map/BSS counters, and compares packet/byte totals.

Control flow: setup cgroup and skeleton, attach ingress/egress accounting programs, run traffic, read counters, assert nonzero/expected deltas, detach and cleanup.

State and persistence: cgroup attachment and accounting maps are transient. Counter values are the tested state.

Dependencies and integration: depends on cgroup helpers, network helpers, `netcnt.skel.h`, and predictable local traffic.

Risks and test signals: packet/byte counters matching generated traffic are signals. Risks include traffic offload/path differences, cgroup join failure, and counter races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/netcnt.c -->
