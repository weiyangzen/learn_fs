# sources/distributed-fs/ceph-client/arch/parisc/math-emu/driver.c

Purpose: connects the Linux PA-RISC floating-point exception path to the software emulator.

Important APIs/types/functions: `int handle_fpe(struct pt_regs *regs)` copies the saved floating-point register file, invokes `decode_fpu()`, writes modified registers back, and sends a Unix signal if required. Local macros decode instruction bit fields but are largely unused in this file.

Control flow: `handle_fpe()` copies `regs->fr` into a 36-entry local `frcopy` because the emulator expects extra scratch/type entries. It saves the original status word for optional debug output, calls `decode_fpu(frcopy, 0x666)`, copies the emulated register image back to `regs->fr`, and if a signal code is returned, clears the floating-point trap bit for `SIGFPE` before calling `force_sig_fault()` at the current instruction address.

State and dependencies: mutates the interrupted task's floating-point registers and may deliver a signal. Depends on `pt_regs`, `linux/sched/signal.h`, `math-emu.h`, `decode_fpu`, and debug-only `printbinary`.

Risks: register image sizing and layout must match both kernel save state and emulator expectations. Passing `0x666` as `trap_counts` relies on `decode_fpu` not dereferencing it meaningfully. Trap-bit clearing is necessary to avoid recursive user signal-handler traps.

Test signals: user programs that execute unsupported FPU instructions, signal delivery tests for `SIGFPE` and `SIGILL`, register preservation tests, and debug-disabled build coverage.
