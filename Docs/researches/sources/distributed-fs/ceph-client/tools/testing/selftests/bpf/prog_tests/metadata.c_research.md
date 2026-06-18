<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/metadata.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/metadata.c

Purpose: tests whether BPF program metadata references keep maps alive only when metadata is actually used.

Important APIs and functions: `prog_holds_map()` compares map IDs reported by `bpf_prog_get_info_by_fd()` against a target map ID from `bpf_map_get_info_by_fd()`. The test loads `metadata_unused` and `metadata_used` skeletons, attaches programs, triggers cgroup/network activity, and checks program map references.

Control flow: for unused metadata, the program should not hold the metadata map. For used metadata, the program should report the map in `nr_map_ids`. Cgroup and socket helpers provide trigger context, then resources are closed.

State and persistence: map/program fds and cgroup attachment are temporary. The tested state is kernel-reported program-to-map ID references.

Dependencies and integration: depends on `metadata_unused.skel.h`, `metadata_used.skel.h`, cgroup helpers, network helpers, and BPF info syscalls.

Risks and test signals: presence or absence of the metadata map ID in program info is the signal. Risks are changes in kernel info reporting or compiler optimization of metadata references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/metadata.c -->
