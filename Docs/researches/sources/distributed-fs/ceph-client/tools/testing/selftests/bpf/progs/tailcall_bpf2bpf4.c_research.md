<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf4.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf4.c

Purpose: Stress test for tail calls from subprograms with extra map lookups and chained target programs.

Important APIs/types/functions: Defines `nop_table`, `jmp_table`, globals `count`/`noise`, subprograms `subprog_tail*`, classifiers 0/1/2, and entry.

Control flow: Entry calls `subprog_tail`, which tail-calls index 0; targets call deeper subprograms and may use `nop_table` before further tail calls.

State and persistence: Persistent state includes prog-array, nop array, and global counters.

Dependencies and integration: Depends on BPF-to-BPF calls, map lookups, static tail calls, and tc context.

Risks: JIT patching must survive subprograms with unrelated helper calls and counter mutation.

Test signals: Tests verify expected chain depth, counter increments, and fallback values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf4.c -->
