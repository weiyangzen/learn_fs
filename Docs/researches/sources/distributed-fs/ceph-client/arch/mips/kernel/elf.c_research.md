<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/elf.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/elf.c

### Purpose
`elf.c` validates and applies MIPS-specific ELF ABI properties, especially FPU ABI mode, NaN encoding personality, and read-implies-exec behavior.

### Important APIs, Types, And Functions
Important globals are `mips_use_nan_legacy` and `mips_use_nan_2008`. Key functions are `arch_elf_pt_proc()`, `arch_check_elf()`, `set_thread_fp_mode()`, `mips_set_personality_fp()`, `mips_set_personality_nan()`, and exported `mips_elf_read_implies_exec()`.

### Control Flow
Program-header processing reads `PT_MIPS_ABIFLAGS` and records program/interpreter FP ABIs. ELF check validates NaN2008 compatibility, enforces matching interpreter NaN mode, computes allowable FP mode for O32 FP64 support, and rejects incompatible ABI combinations. Personality setup writes thread FP mode flags and FCSR NaN/ABS mode. Read-implies-exec is set only on CPUs lacking RIXI when `PT_GNU_STACK` did not specify a state.

### State, Persistence, And Dependencies
State is per-exec `arch_elf_state`, current thread flags, task FPU FCSR, global NaN policy, CPU FPU capabilities, and ELF flags. Dependencies include binfmt ELF, MIPS ABI flags, FPU ownership helpers, and CPU feature data.

### Integration Points
The Linux ELF loader calls these hooks during exec. Signal/FPU context, VDSO, user ABI compatibility, and security executable-stack policy depend on the decisions.

### Risks
O32 FP mode compatibility is subtle, especially with interpreters. Incorrect NaN policy can allow binaries that produce incompatible floating-point semantics. `kernel_read()` failures in ABI flags must propagate correctly.

### Test Signals
Exec tests for FP32/FP64/FPXX/soft-float/unknown ABI, interpreter mismatch, NaN2008 vs legacy policy, FCSR initialization, thread flags, and read-implies-exec on RIXI/non-RIXI CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/elf.c -->
