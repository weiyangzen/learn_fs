<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/fpu.S -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/fpu.S

Purpose: implements low-level save, restore, initialize, and signal-copy routines for LoongArch FPU, LSX, and LASX register state.
Important APIs and types: exports `_save_fp`, `_save_lsx`, `_save_lasx`, `_restore_lsx_upper`, `_restore_lasx_upper`, and defines `_restore_fp`, `_restore_lsx`, `_restore_lasx`, `_init_fpu`, `_init_lsx_upper`, `_init_lasx_upper`, plus exception-table guarded `sc_save_*`/`sc_restore_*` macros for signal contexts.
Control flow: context switch, signal, ptrace, and debug paths call assembly routines to move FPU/vector registers to/from `thread_struct` or user signal context buffers. Exception table entries route faulting user-context loads/stores to a common fault return.
State and persistence: persists floating-point control/status, FCC flags, 32 FPRs, LSX 128-bit vector state, and LASX 256-bit vector state in task structures and signal frames.
Dependencies and integration: depends on asm offsets, FPU/vector register definitions, exception tables, signal context layout, lazy FPU enable, and CPU feature config.
Risks and test signals: offset/register-order mistakes leak or corrupt FPU/vector state. Signals include FPU math tests, LSX/LASX context-switch stress, signal save/restore, ptrace register access, and fault injection on signal frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/fpu.S -->
