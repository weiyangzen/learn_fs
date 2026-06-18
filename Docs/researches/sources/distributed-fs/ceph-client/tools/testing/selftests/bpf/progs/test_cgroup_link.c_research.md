<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cgroup_link.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cgroup_link.c

Purpose: Minimal cgroup skb link test with alternate egress programs.

Important APIs/types/functions: Defines `egress` and `egress_alt` in `cgroup_skb/egress` sections.

Control flow: Programs return simple verdicts so userspace can update/replace cgroup links.

State and persistence: No persistent maps.

Dependencies and integration: Depends on cgroup skb attach/link update APIs.

Risks: Link replacement must swap active program without stale execution.

Test signals: Tests attach both programs and verify egress verdict changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cgroup_link.c -->
