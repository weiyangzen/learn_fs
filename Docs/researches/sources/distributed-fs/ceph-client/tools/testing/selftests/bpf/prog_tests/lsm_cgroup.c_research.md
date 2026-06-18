<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lsm_cgroup.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lsm_cgroup.c

Purpose: validates cgroup-scoped BPF LSM attachment, query, stacking, detach, and enforcement behavior for socket hooks.

Important APIs and functions: `query_prog_cnt()` uses BTF to resolve LSM attach function IDs and `bpf_prog_query_opts()` to count attached programs. `test_lsm_cgroup_functional()` creates cgroups, loads `lsm_cgroup`, attaches programs through links and `bpf_prog_attach`, exercises socket create/bind/listen/connect/accept paths, checks socket priority and BSS counters, then detaches selected programs. `test_lsm_cgroup_nonvoid()` ensures non-void cgroup LSM programs are rejected.

Control flow: setup cgroups and skeleton, attach LSM programs to multiple cgroups, verify query counts, exercise sockets in target cgroups, verify hooks ran the expected number of times, join an empty cgroup to prove isolation, detach/close/destroy. The top-level runs `functional` and `nonvoid`.

State and persistence: cgroup fds, BPF links, direct cgroup attachments, sockets, and BSS counters are transient. One bind link is intentionally left for cgroup-release cleanup coverage.

Dependencies and integration: depends on BTF, cgroup helpers, network helpers, `lsm_cgroup.skel.h`, `lsm_cgroup_nonvoid.skel.h`, and kernel support for `BPF_LSM_CGROUP`.

Risks and test signals: hook counters such as socket allocation/copy counts and socket priority changes signal success. Risks include BTF attach function lookup failures, cgroup cleanup behavior, and subtle attach/detach stacking regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lsm_cgroup.c -->
