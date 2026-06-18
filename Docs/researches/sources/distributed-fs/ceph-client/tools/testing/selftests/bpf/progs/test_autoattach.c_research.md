<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_autoattach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_autoattach.c

Purpose: Minimal raw tracepoint auto-attach test.

Important APIs/types/functions: Defines `prog1` on `raw_tp/sys_enter` and `prog2` on `raw_tp/sys_exit`.

Control flow: Each program runs when its raw tracepoint fires.

State and persistence: No maps; globals or invocation counts are external to this file.

Dependencies and integration: Depends on libbpf auto-attach section names for raw tracepoints.

Risks: Section parsing regression would skip one hook.

Test signals: Test signal is successful auto-attach and trigger of both tracepoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_autoattach.c -->
