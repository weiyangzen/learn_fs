# sources/distributed-fs/ceph-client/arch/sparc/math-emu/math_64.c

Purpose: SPARC64 software floating-point emulator for unfinished/unimplemented FPop traps and illegal-instruction cases on newer sun4v CPUs. It handles quad operations, subnormal single/double operations, conversions, comparisons, and conditional quad moves.

Important APIs/functions: `do_mathemu(struct pt_regs *regs, struct fpustate *f, bool illegal_insn_trap)` is the entry point. `record_exception(struct pt_regs *regs, int eflag)` updates `current_thread_info()->xfsr[0]` and advances `tpc/tnpc` when no trap is generated. Opcode constants include FPOP1 quad/subnormal operations, FPOP2 compares, and conditional `fmovq` forms. It uses FPRS flags `FPRS_DL`, `FPRS_DU`, and `FPRS_FEF` to manage lazy FPU register state.

Control flow: the entry rejects privileged unfinished FPop by dying in kernel mode, records a perf emulation fault, adjusts PC for 32-bit tasks, fetches the user instruction, and decodes FPOP1/FPOP2. Conditional quad moves evaluate floating condition codes, integer condition codes, or register-zero/less-than conditions; false conditions become a nop that clears CEXC and advances PC, true conditions are rewritten as plain `fmovq`. For decoded operations, the routine validates trap type unless invoked via illegal instruction, maps encoded register numbers into SPARC64 FP register storage, substitutes zero for unsaved halves, initializes FPRS state for destinations, executes soft-fp macros, writes results or condition codes, records exceptions, and advances `tpc/tnpc` on success.

State and persistence: mutates `current_thread_info()->xfsr[0]`, `fpsaved[0]`, `gsr[0]`, `regs->tpc/tnpc`, and the supplied `fpustate` register file. It may flush user register windows to read locals for register-conditional moves. Exception and lazy-FPU state persist in thread info.

Dependencies/integration: includes `asm/fpumacro.h`, `asm/cacheflush.h`, `linux/uaccess.h`, `sfp-util_64.h`, and soft-fp headers. Integrates with trap handlers for unfinished FPop, unimplemented FPop, and UltraSPARC-T2 illegal instruction behavior.

Risks: register renumbering for 64-bit FP regs (`((freg & 1) << 5) | (freg & 0x1e)`) is easy to break. Conditional move paths read user register windows and must handle 32-bit vs 64-bit stack windows correctly. Trap-type validation differs for illegal-instruction traps, so caller classification matters. Lazy FPRS initialization can zero half the FP register file if flags are wrong.

Test signals: SPARC64 FP emulation tests for quad arithmetic/move/compare, subnormal single/double operations, 32-bit task PCs, all conditional `fmovq` condition sources, invalid register encodings, FPRS lazy state, and T2 illegal-instruction trap paths. User FP workloads forcing subnormal/quad software paths are key integration tests.
