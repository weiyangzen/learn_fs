<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_kernel.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_kernel.c

Purpose: Kernel CO-RE test reading current task fields and long nested `group_leader` chains.

Important APIs/types/functions: Defines local `task_struct` flavors, output struct, and raw tracepoint `test_core_kernel`.

Control flow: Handler gates on `my_pid_tgid`, reads pid/tgid, uses variadic `BPF_CORE_READ` up to deep nesting, reads comm string, and checks type matching when clang supports it.

State and persistence: Persistent state is the `data` global with input pid, skip flag, and output buffer.

Dependencies and integration: Depends on kernel BTF, `bpf_get_current_task`, `BPF_CORE_READ`, `BPF_CORE_READ_STR_INTO`, and clang preserve-type-info support.

Risks: Toolchain feature gating, deep relocation chains, and local type mismatch handling are risks.

Test signals: Tests set pid, trigger sys_enter, and validate all `valid[]`, comm length, and type-match/skip fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_core_reloc_kernel.c -->
