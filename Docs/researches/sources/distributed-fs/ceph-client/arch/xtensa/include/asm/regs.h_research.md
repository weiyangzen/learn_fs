<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/regs.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/regs.h

Purpose: centralizes Xtensa special register numbers and bitfield constants for exception causes, processor status, debug break controls, and debug cause decoding. Important constants include `SREG_*` register bases, `EXCCAUSE_*` enumerations, `PS_*` masks/shifts, `DBREAKC_*` masks, and `DEBUGCAUSE_*` masks/bits.

Control flow is absent; this file is a shared ABI between C and assembly. State described by the constants is hardware state in PS, EXCCAUSE, DEBUGCAUSE, IBREAK/DBREAK, EPC/EPS/EXCSAVE, CCOMPARE, and related registers. Dependencies are minimal, but consumers rely on Xtensa ISA and configured register counts. Integration points include low-level exception entry, debug exception handling, hardware breakpoints, PMU, time, boot code, and trap dispatch. Risks are incorrect bit definitions causing unrecoverable exception handling, missed debug/watchpoint events, or wrong interrupt masking. Test signals include build coverage across hardware variants, hardware breakpoint tests, exception cause routing, timer interrupts, and debug single-step/watchpoint validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/regs.h -->
