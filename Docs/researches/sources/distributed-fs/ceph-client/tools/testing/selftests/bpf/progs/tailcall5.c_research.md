<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall5.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall5.c

Purpose: Tail-call test variant covering static call behavior with a different map capacity/control path.

Important APIs/types/functions: Defines `jmp_table` and tc entry/classifier programs.

Control flow: The entry path attempts static tail calls and returns a fallback if no transfer occurs.

State and persistence: Only prog-array state persists.

Dependencies and integration: Depends on BPF prog-array and static tail-call patching.

Risks: Wrong max_entries or key relocation can reject or misroute calls.

Test signals: Return-code checks after populating the map are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall5.c -->
