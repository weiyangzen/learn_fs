<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall1.c

Purpose: Tests static tail-call patching when the same prog-array index appears at many call sites.

Important APIs/types/functions: Defines `jmp_table`, three tc classifiers returning 0/1/2, and `entry` with repeated static calls to indexes 0, 1, and 2.

Control flow: `entry` attempts each static tail call in order; a successful tail call transfers to the target classifier, otherwise it eventually returns 3.

State and persistence: Persistent state is the prog-array map populated by userspace.

Dependencies and integration: Depends on static tail-call patching in tc programs.

Risks: All call sites for the same index must be patched consistently.

Test signals: Tests populate indexes and assert observed return values match the selected classifier or fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall1.c -->
