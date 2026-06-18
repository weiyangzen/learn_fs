# sources/distributed-fs/ceph-client/arch/sparc/math-emu/math_32.c

Purpose: SPARC32 software floating-point instruction emulator. It decodes trapped FPOP instructions, runs Linux soft-fp operations, updates task FPU state, and reports whether a SIGFPE-style trap is required.

Important APIs/functions: `do_mathemu(struct pt_regs *regs, struct task_struct *fpt)` is the entry point. `record_exception(unsigned long *pfsr, int eflag)` updates FSR CEXC/AEXC/TEM/trap-type fields. `do_one_mathemu(u32 insn, unsigned long *pfsr, unsigned long *fregs)` decodes one instruction and dispatches to soft-fp macros. Opcode constants cover V8 single, double, quad, conversion, move, sqrt, and compare instructions. `argp` overlays raw register storage as single/double/quad.

Control flow: `do_mathemu` records an emulation perf event, either fetches the precise instruction from `regs->pc` when the FP queue is empty or iterates queued instructions from `thread.fpqueue`. On success for a precise trap it advances `pc/npc`; for queued traps it clears queue flags and `fpqdepth`. `do_one_mathemu` classifies FPOP1/FPOP2 opcodes into a packed `type`, validates register alignment for double/quad operands, unpacks operands with soft-fp macros, executes the requested arithmetic/conversion/compare, packs results unless `FP_INHIBIT_RESULTS`, and records exceptions.

State and persistence: mutates `fpt->thread.fsr`, `fpt->thread.float_regs`, `fpt->thread.fpqdepth`, and possibly `regs->pc/npc`. No heap state. Exception state persists in FSR accrued/current exception bits.

Dependencies/integration: includes scheduler/MM/uaccess/perf headers, `sfp-util_32.h`, and the generic `math-emu/soft-fp`, `single`, `double`, and `quad` macro layers. Trap handling supplies the task owning the FPU, which may not be `current`.

Risks: FPU queue handling is architecturally delicate; a failed queued instruction stops further emulation but still clears queue metadata. Register alignment checks determine whether invalid_fp_register is simulated. Soft-fp exception prioritization must match SPARC hardware, especially compare-with-NaN and trap-enabled TEM cases. `get_user` fetch failures return failure without advancing PC.

Test signals: SPARC32 FP emulation tests for all decoded opcodes, invalid register numbers, precise and queued traps, all IEEE exception classes with TEM enabled/disabled, NaN compare cases, and PC/nPC advancement. Perf software emulation fault counters should increment. Running floating-point workloads on systems with disabled/missing FPU is the integration signal.
