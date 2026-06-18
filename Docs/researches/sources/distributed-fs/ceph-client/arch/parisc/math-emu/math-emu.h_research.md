# sources/distributed-fs/ceph-client/arch/parisc/math-emu/math-emu.h

Purpose: exposes the PA-RISC floating-point exception handler entry point to the rest of the architecture code.

Important API: `extern int handle_fpe(struct pt_regs *regs);` declares the handler that receives trap register state and coordinates floating-point emulation.

Control flow: this header has no executable logic. It includes `<asm/ptrace.h>` so the declaration can name `struct pt_regs`. Kernel trap code includes it before calling `handle_fpe()` for FP assist and emulation traps.

State and persistence: no state. The persistent contract is the function signature shared between `arch/parisc/kernel/traps.c` and `arch/parisc/math-emu/driver.c`.

Dependencies and integration: links the math-emulation directory to the architecture trap layer. `driver.c` supplies the implementation, which then reaches `decode_exc.c` and `fpudispatch.c`.

Risks: signature drift would break the trap integration. Because the handler receives mutable register state, callers and implementation must agree on PA-RISC `pt_regs` layout and trap return semantics.

Test signals: build with `CONFIG_MATH_EMULATION`, trigger a floating-point assist exception, verify `handle_fpe()` is called from traps, and check that user-visible signals or emulated instruction completion match hardware behavior.
