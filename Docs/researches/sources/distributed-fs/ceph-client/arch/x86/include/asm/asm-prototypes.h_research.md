
# sources/distributed-fs/ceph-client/arch/x86/include/asm/asm-prototypes.h

Purpose: collects C prototypes and includes needed by assembly-exported x86 symbols and modversion generation.

Important APIs and control flow: it includes ftrace, uaccess, pgtable, string, page, checksum, MCE, generic asm prototypes, special instructions, preempt, FRED, GS segment, and nospec branch headers. It declares `cmpxchg8b_emu()` when CX8 is not guaranteed and exposes `__ref_stack_chk_guard` for stack protector builds.

State, dependencies, and risks: no direct runtime state, but it is a build ABI surface between assembly and C. Dependencies span low-level x86 subsystems. Risks are missing prototypes causing modversion or linkage drift, especially for assembly routines with C callers. Test signals are allmodconfig/modversion builds, non-CX8 32-bit builds, and stack-protector link coverage.
