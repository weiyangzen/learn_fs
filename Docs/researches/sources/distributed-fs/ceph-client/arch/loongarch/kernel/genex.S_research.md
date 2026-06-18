<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/genex.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/genex.S

Purpose: defines general LoongArch exception vectors and exception handler stubs.
Important APIs and types: implements `__arch_cpu_idle`, `handle_vint`, `except_vec_cex`, `handle_ade`, `handle_ale`, `handle_bce`, `handle_bp`, `handle_fpe`, `handle_fpu`, `handle_lsx`, `handle_lasx`, `handle_lbt`, `handle_ri`, `handle_watch`, `handle_reserved`, and `handle_sys`.
Control flow: vector stubs save state with `SAVE_ALL`, prepare BADV/FCSR arguments when needed, call C `do_*` handlers, then restore all registers. `handle_vint` handles the idle interrupt window specially so an interrupt between enabling IRQs and `idle` does not re-enter idle.
State and persistence: creates transient `pt_regs` frames and emits unwind hint metadata for exception frames.
Dependencies and integration: depends on `stackframe.h`, `thread_info.h`, CSR definitions, C trap handlers, idle code, KGDB/kprobe break handling, and interrupt dispatch.
Risks and test signals: wrong save/restore or idle-window handling causes interrupt loss or register corruption. Signals include interrupt storm tests, exception/fault tests, idle/reschedule behavior, KGDB/kprobe/uprobe breakpoints, and unwinder validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/genex.S -->
