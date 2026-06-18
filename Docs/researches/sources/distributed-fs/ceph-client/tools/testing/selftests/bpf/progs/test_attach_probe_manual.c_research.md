<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_probe_manual.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_probe_manual.c

Purpose: Manual attach counterpart for kprobe, kretprobe, uprobe, and uretprobe programs.

Important APIs/types/functions: Defines simple handlers for each probe kind with generic section names.

Control flow: Userspace manually attaches each program to target symbols/functions; handlers update or return known values.

State and persistence: No maps; result globals track invocation.

Dependencies and integration: Depends on manual libbpf attach APIs and probe program types.

Risks: Wrong attach target or program type mismatch causes silent non-invocation.

Test signals: Tests attach manually and verify each handler ran.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_probe_manual.c -->
