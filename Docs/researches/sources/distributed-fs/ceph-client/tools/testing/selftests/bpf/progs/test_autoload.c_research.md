<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_autoload.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_autoload.c

Purpose: Tests libbpf autoload control with loadable and intentionally missing fentry targets.

Important APIs/types/functions: Defines raw tracepoint programs `prog1`/`prog2`, an fentry program `prog3` for a non-existing target, and a fake struct.

Control flow: Userspace disables autoload or expects failure depending on program selection.

State and persistence: No runtime state beyond loaded programs.

Dependencies and integration: Depends on libbpf autoload flags and attach target resolution.

Risks: A disabled failing program must not prevent object load.

Test signals: Tests toggle autoload and confirm only expected programs load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_autoload.c -->
