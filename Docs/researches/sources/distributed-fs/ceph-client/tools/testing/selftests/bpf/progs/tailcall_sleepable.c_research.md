<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_sleepable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_sleepable.c

Purpose: Checks tail-call behavior between normal and sleepable uprobe programs.

Important APIs/types/functions: Defines a one-entry `jmp_table`, optional normal and sleepable uprobes, plus globals `executed` and `my_pid`.

Control flow: Normal and sleepable programs attempt tail calls; `uprobe_sleepable_2` increments `executed` only for `my_pid`.

State and persistence: Persistent state is prog-array plus execution counters.

Dependencies and integration: Depends on sleepable uprobe sections and tail-call compatibility rules.

Risks: Tail calls between sleepable and non-sleepable contexts must enforce program-type constraints.

Test signals: Tests set `my_pid`, trigger uprobes, and inspect `executed`/load outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/tailcall_sleepable.c -->
