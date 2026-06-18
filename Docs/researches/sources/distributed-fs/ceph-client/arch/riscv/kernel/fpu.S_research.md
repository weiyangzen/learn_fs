# sources/distributed-fs/ceph-client/arch/riscv/kernel/fpu.S

Purpose: Saves/restores RISC-V floating-point state and provides debugger/register access helpers for FP registers.

Important APIs/types/functions: Defines `__fstate_save`, `__fstate_restore`, `put_f32_reg`, `get_f32_reg`, `put_f64_reg`, `get_f64_reg`, plus access prologue/epilogue macros.

Control flow: Save/restore routines enable FP access as needed, move all FP registers and `fcsr` to or from task storage, then restore status bits. Get/put helpers temporarily enable FP state and move one register between memory and hardware.

State and persistence: Persists user FP state in task `__riscv_d_ext_state` storage and manipulates `sstatus.FS`/`fcsr`.

Dependencies and integration points: Used by switch-to, signal, ptrace, KGDB, and kernel FP wrappers; depends on F/D extension availability and `asm-offsets`.

Risks and test signals: Lazy FP state, fcsr preservation, and register width handling are ABI-visible. Test FP context switching, signal save/restore, ptrace register reads/writes, preemption around kernel FP use, and RV32/RV64 builds.
