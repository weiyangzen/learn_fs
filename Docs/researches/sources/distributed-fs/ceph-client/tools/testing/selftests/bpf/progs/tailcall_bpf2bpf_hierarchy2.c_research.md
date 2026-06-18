<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy2.c

Purpose: Hierarchy test with two auxiliary tc classifiers that recursively tail-call themselves through a static prog-array.

Important APIs/types/functions: Defines initialized `jmp_table`, counters `count0`/`count1`, `subprog_tail0/1`, auxiliary classifiers, and main `tailcall_bpf2bpf_hierarchy_2` with expected retval 33.

Control flow: Main calls both subprograms after clobbering registers/stack; each target increments a counter and attempts another tail call until limits apply.

State and persistence: Counters and initialized prog-array are persistent state.

Dependencies and integration: Depends on auxiliary program sections, static prog-array values, and tail-call limit accounting.

Risks: Register clobbering and recursive hierarchy must not corrupt tail-call count or stack state.

Test signals: Pass signal is verifier success and return value `(count1 << 16) | count0 == 33`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_bpf2bpf_hierarchy2.c -->
