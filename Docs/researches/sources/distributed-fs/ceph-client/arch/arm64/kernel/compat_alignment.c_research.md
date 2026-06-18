<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/compat_alignment.c -->
## sources/distributed-fs/ceph-client/arch/arm64/kernel/compat_alignment.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/compat_alignment.c` handles unaligned memory-access fixups for 32-bit compat tasks on arm64 when compatibility alignment fixups are enabled. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `CODING_BITS`, `LDST_P_BIT`, `LDST_U_BIT`, `LDST_W_BIT`, `LDST_L_BIT`, `LDST_P_EQ_U`, `LDSTHD_I_BIT`, `RN_BITS`, `RD_BITS`, `RM_BITS`, `REGMASK_BITS`, `BAD_INSTR`, `IS_T32`, `TYPE_ERROR`, `TYPE_FAULT`, `TYPE_LDST`, `TYPE_DONE`; types: `offset_union`, `pt_regs`; functions/prototypes/exports: `do_alignment_finish_ldst`, `do_alignment_ldrdstrd`, `do_alignment_ldmstm`, `thumb2arm`, `do_alignment_t32_to_handler`, `alignment_get_arm`, `alignment_get_thumb`, `do_compat_alignment_fixup`. The file is 385 lines / 10056 bytes. Direct includes are `linux/compiler.h`, `linux/errno.h`, `linux/kernel.h`, `linux/init.h`, `linux/perf_event.h`, `linux/uaccess.h`, `asm/exception.h`, `asm/ptrace.h`, `asm/traps.h`.

### Control Flow
Fault handling fetches ARM or Thumb instructions from userspace, decodes load/store forms, translates supported Thumb encodings, performs aligned user accesses, updates registers/writeback, and advances the faulting PC.

### State, Persistence, And Dependencies
Notable global/static state symbols are `do_alignment_ldrdstrd`, `rd`, `rd2`, `load`, `val`, `do_alignment_ldmstm`, `L`, `Rn`, `W`, `subset`, `instr`, `alignment_get_arm`, `fault`, `alignment_get_thumb`, `do_compat_alignment_fixup`, `type`, `isize`, `thumb2_32b`. State changes are limited to the compat task's pt_regs and target user memory for emulated stores. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Decoder gaps, wrong writeback, user access faults, or endian/register-list mistakes can corrupt compat process state or loop on faults.

### Test Signals
Run AArch32 unaligned access tests for ARM and Thumb, multi-register transfers, fault injection, signal interaction, and perf alignment-event checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kernel/compat_alignment.c -->
