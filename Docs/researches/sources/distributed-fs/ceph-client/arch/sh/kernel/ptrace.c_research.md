# sources/distributed-fs/ceph-client/arch/sh/kernel/ptrace.c

Purpose: provides generic SH helpers for mapping register names to `struct pt_regs` offsets and back.

Important APIs and control flow: `regs_query_register_offset()` linearly searches `regoffset_table` for a name and returns the offset or `-EINVAL`. `regs_query_register_name()` searches for an offset and returns the name or `NULL`.

State, dependencies, and risks: state is the `regoffset_table` defined in the 32-bit ptrace implementation. Dependencies include exact `pt_regs` field offsets and Linux register query APIs used by tracing/kprobes/perf tooling. Risks are stale table entries when `pt_regs` changes and linear lookup cost is trivial but unindexed. Test signals are kprobe/ftrace register-name queries and ptrace/debugger register offset validation.
