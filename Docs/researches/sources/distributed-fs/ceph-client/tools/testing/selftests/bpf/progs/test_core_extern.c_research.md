<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_extern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_extern.c

Purpose: Tests CO-RE extern variables, especially kconfig extern resolution.

Important APIs/types/functions: Defines extern-like globals and raw tracepoint `handle_sys_enter`.

Control flow: Handler reads extern values and records which externs were resolved or defaulted.

State and persistence: State is BSS result globals.

Dependencies and integration: Depends on libbpf extern/kconfig CO-RE relocation.

Risks: Missing externs must follow expected optional/default semantics.

Test signals: Tests inspect loaded global values after triggering sys_enter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_extern.c -->
