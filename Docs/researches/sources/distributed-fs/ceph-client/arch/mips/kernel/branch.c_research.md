<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/branch.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/branch.c

### Purpose
`branch.c` decodes MIPS, microMIPS, MIPS16e, DSP, FPU, Octeon, and MIPS R6 branch instructions to compute the correct exception return EPC after faults in delay or forbidden slots.

### Important APIs, Types, And Functions
Core functions are `__isa_exception_epc()`, `__mm_isBranchInstr()`, `__microMIPS_compute_return_epc()`, `__MIPS16e_compute_return_epc()`, `__compute_return_epc_for_insn()`, exported `__compute_return_epc()`, and exported `__insn_is_compact_branch()` for kprobes/uprobes.

### Control Flow
The code fetches the instruction at EPC, handles ISA16 mode separately, decodes opcode/function fields, evaluates register/FPU/DSP conditions, sets link registers for call branches, updates `regs->cp0_epc`, and returns whether a branch-likely delay slot was taken. Illegal ISA combinations force `SIGILL`; failed instruction fetches force `SIGSEGV`; unaligned EPC forces `SIGBUS`.

### State, Persistence, And Dependencies
State is the live `pt_regs`, current task FPU state, CP1 status, DSP control register, and CPU feature flags. Dependencies include instruction format definitions, FPU ownership helpers, R2-to-R6 emulation flags, user access, and signal delivery.

### Integration Points
Exception handling, unaligned access emulation, FPU emulation, kprobes/uprobes, and signal generation use this logic to resume correctly after branch delay slot faults.

### Risks
Branch decoding is architecture-sensitive and easy to regress for compact branches, link register updates, ISA mode bits, and branch-likely return values. The R6 compact branch section for `bgtz` tests `blez_op` in one link-register condition, which deserves scrutiny against the ISA comments.

### Test Signals
Instruction-level tests should fault every branch form in delay/forbidden slots across MIPS32/64, microMIPS, MIPS16e, R6 compact branches, DSP `bposge32`, FPU condition branches, and Octeon bit branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/branch.c -->
