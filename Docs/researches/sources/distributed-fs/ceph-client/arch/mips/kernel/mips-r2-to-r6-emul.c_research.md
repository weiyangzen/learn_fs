<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-r2-to-r6-emul.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/mips-r2-to-r6-emul.c

### Purpose
`mips-r2-to-r6-emul.c` emulates user-space MIPS R2/R5 instructions removed or changed by MIPS R6. It lets older binaries run on R6 CPUs by handling reserved-instruction traps, emulating arithmetic, branch-likely delay-slot behavior, unaligned load/store forms, LL/SC, and FPU instructions, with optional debugfs statistics.

### Important APIs, Types, And Functions
The main exported decoder is `mipsr2_decoder(struct pt_regs *regs, u32 inst, unsigned long *fcr31)`. Boot option `mipsr2emu` enables `mipsr2_emulation`. Important helpers include `mipsr6_emul()` for fast delay-slot emulation, instruction-specific functions such as `jr_func()`, `movf_func()`, `movt_func()`, `movz_func()`, `mfhi_func()`, `mult_func()`, `div_func()`, `dmult_func()`, `madd_func()`, `mul_func()`, `clz_func()`, and decoder tables `spec_op_table` and `spec2_op_table`. Debugfs show functions expose and clear per-CPU counters.

### Control Flow
The decoder computes the normal return EPC, switches on opcode, emulates SPECIAL/SPECIAL2 functions through mask/code tables, handles branch-likely and link branches by recomputing target EPC and emulating or trampoline-running delay-slot instructions, delegates FPU opcodes to `fpu_emulator_cop1Handler()`, implements left/right word/doubleword loads and stores with endian-specific byte assembly, emulates LL/SC only when `cpu_has_rw_llb`, and skips PREF. After a successful instruction it attempts up to `MIPS_R2_EMUL_TOTAL_PASS` sequential emulations before returning to user mode.

### State, Persistence, And Dependencies
State is modified in `pt_regs` general registers, HI/LO, EPC, Cause BD bit, current task FPU state, `thread.cp0_baduaddr`, and optional per-CPU debugfs counters. Dependencies include MIPS instruction macros, branch EPC computation, user access/ex-table fixups, FPU emulator, `mips_dsemul()`, Config5 LLB support, debugfs, and endian/32-bit/64-bit config guards.

### Integration Points
This file is called from reserved-instruction handling for user mode on R6-capable systems. It integrates with FPU emulation, delay-slot emulation, signal delivery by returning SIG* values, and `mips_debugfs_dir` for observability.

### Risks
Instruction semantics must exactly match older ISA behavior, including sign extension, zero-register writes, delay-slot branch-likely nullification, and endian-specific unaligned memory byte order. Division by zero follows hardware-like behavior only if callers expect it. LL/SC emulation without Config5 LLB is intentionally fatal because atomicity cannot be preserved.

### Test Signals
Run old R2/R5 user-space ISA tests on R6 hardware or QEMU, including MOVF/MOVT, HI/LO ops, multiply/divide, DSP-like MADD/MSUB, branch-likely delay slots, JR with delay slots, unaligned LWL/LWR/SWL/SWR and LDL/LDR/SDL/SDR on both endian modes, LL/SC atomics, FPU traps, SIGSEGV/SIGBUS fault paths, and debugfs counter clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/mips-r2-to-r6-emul.c -->
