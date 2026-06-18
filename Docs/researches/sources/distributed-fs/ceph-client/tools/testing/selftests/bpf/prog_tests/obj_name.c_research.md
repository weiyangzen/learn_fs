<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/obj_name.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/obj_name.c

Purpose: tests allowed and rejected BPF object names for maps/programs, including length and character constraints.

Important APIs and functions: the harness creates BPF maps/programs or opens skeleton variants with specific names, then checks success or expected errors.

Control flow: iterate valid and invalid names, attempt object creation/load, assert success for accepted names and failure for rejected ones, close fds.

State and persistence: only temporary BPF fds are created. Invalid cases should leave no persistent objects.

Dependencies and integration: depends on BPF object naming rules in the kernel and libbpf syscall wrappers.

Risks and test signals: expected accept/reject outcomes and errno values are signals. Risks are naming policy changes or libbpf pre-validation differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/obj_name.c -->
