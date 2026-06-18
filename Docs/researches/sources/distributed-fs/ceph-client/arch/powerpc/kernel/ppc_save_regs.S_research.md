# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ppc_save_regs.S

Purpose: this assembly helper snapshots the current PowerPC register state into a `pt_regs`-shaped buffer for diagnostic or low-level callers. It is explicitly approximate because the caller's prologue has already modified some state before this function can save it.

Important API: `_GLOBAL(ppc_save_regs)` expects `r3` to point past the interrupt-frame register area, then subtracts `STACK_INT_FRAME_REGS` so standard `pt_regs` offsets can be used. It stores general-purpose registers, stack pointer, caller link register, current NIP, MSR, CTR, XER, CCR, and clears trap/original GPR3 fields. On 64-bit it also stores PACA soft interrupt mask in `SOFTE`; on 32-bit it uses `stmw` for GPR2 and above.

Control flow: the function adjusts the destination pointer, saves volatile and nonvolatile GPRs using ABI-specific macros, records `r1` as the current stack pointer, walks the caller stack frame to recover the caller's saved LR, records its own LR as NIP, reads machine state registers, writes zero for synthetic fields, and returns with `blr`.

State and persistence: it does not modify global state. The persistent effect is the filled caller-provided buffer. It reads architectural registers and, on 64-bit, the PACA soft-mask byte through `r13`.

Dependencies and integration points: depends on PowerPC stack-frame layout, `asm-offsets.h` `pt_regs` offsets, `ppc_asm.h` save macros, `asm-compat.h` load/store width macros, and ABI differences between PPC32 and PPC64. Consumers must provide a buffer large enough for the adjusted frame layout.

Risks: saved state can be misleading because the caller already executed a prologue. Recovering caller LR from stack-frame save area depends on a conventional frame. The function assumes `r3` points to a buffer with enough room before the original address. Architecture offset changes would corrupt the output if not rebuilt consistently.

Test signals: callers should see plausible GPR/MSR/CTR/XER/CCR/NIP/LR values in the resulting `pt_regs`. Build tests across PPC32 and PPC64 are important because register save sequences differ. Runtime tests should verify no buffer underrun and sane stack traces from saved regs.
