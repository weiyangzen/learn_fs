<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/asm-offsets.c

Purpose: Generates assembler-visible offsets and constants for PowerPC low-level assembly from C structure layouts.

Important APIs/types/functions: `STACK_PT_REGS_OFFSET()` and many `OFFSET()`/`DEFINE()` emissions for task/thread, PACA, lppaca, pt_regs, CPU specs, vDSO data, KVM, TM, RTAS, TLB CAM, debug, ftrace, and platform constants.

Control flow: The file is compiled to assembly; kbuild extracts emitted `#define`-style records so assembly files can address C structs safely without hardcoded stale offsets.

State and persistence: No runtime state. Generated offsets persist as build artifacts consumed by assembler.

Dependencies and integration points: Depends on the full set of PowerPC kernel structs and config symbols. Integrated by entry code, KVM handlers, vDSO assembly, suspend/resume, ftrace, and exception paths.

Risks: Missing offsets break assembly builds or, worse, runtime register saves/restores. Config guards must match the assembly consumers.

Test signals: Full architecture builds for PPC32/PPC64, Book3S/BookE, KVM, TM, XMON, ftrace, and suspend configs; inspect generated `asm-offsets.h` when changing structs.

Source read size: 688 lines, 24576 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/asm-offsets.c -->
