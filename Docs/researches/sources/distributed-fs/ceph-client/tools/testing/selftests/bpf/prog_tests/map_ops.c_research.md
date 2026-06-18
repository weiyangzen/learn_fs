<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_ops.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_ops.c

Purpose: validates BPF map operation helpers for update, delete, queue/stack push/pop/peek, and map iteration from instrumented syscall-triggered programs.

Important APIs and functions: small trigger helpers invoke specific syscalls (`getpid`, `getppid`, `getuid`, `geteuid`, `getgid`, `gettid`, `getpgid`). `setup()` opens, loads, and attaches `test_map_ops` with the current PID in rodata. Subtests such as update/delete and queue/stack operations read `skel->bss->err` after each trigger.

Control flow: each subtest creates a fresh skeleton, triggers one or more operations in sequence, checks expected success or errno such as `-EEXIST`, then destroys. The top-level dispatches named subtests.

State and persistence: state is BPF map contents plus BSS error/status fields. Fresh skeletons isolate subtests.

Dependencies and integration: depends on `test_map_ops.skel.h`, syscall trace triggers, and map helper semantics.

Risks and test signals: expected BSS `err` values and map behavior are signals. Risks include syscall attach-point mismatches, map helper errno changes, and queue/stack ordering regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_ops.c -->
