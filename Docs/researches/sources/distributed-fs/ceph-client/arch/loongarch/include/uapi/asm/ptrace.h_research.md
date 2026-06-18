<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/ptrace.h

Purpose: defines LoongArch userspace ptrace register sets and watchpoint state.
Important APIs and types: includes `struct user_pt_regs`, `user_fp_state`, `user_lsx_state`, `user_lasx_state`, `user_lbt_state`, `user_watch_state`, `user_watch_state_v2`, register index constants, and `PTRACE_SYSEMU` requests.
Control flow: ptrace, core dump, signal tooling, debuggers, and BPF use these structures to inspect and modify task state.
State and persistence: structures are UAPI ABI and affect core files, debuggers, and checkpoint/restore.
Dependencies and integration: kernel ptrace code, KGDB/GDB register mapping, perf/BPF, hardware breakpoints, and signal contexts must stay consistent.
Risks and test signals: layout changes break debuggers and CRIU. Signals include ptrace selftests, GDB register access, hardware watchpoint tests, and core dump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/ptrace.h -->
