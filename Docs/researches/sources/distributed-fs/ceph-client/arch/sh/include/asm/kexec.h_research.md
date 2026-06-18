<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kexec.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/asm/kexec.h

## Purpose
Declares SH kexec image limits, machine-kexec entry points, crash preparation, and crash register capture hooks.

## Important APIs, Types, And Functions
Includes `asm/ptrace.h`, `asm/string.h`, `linux/kernel.h`. Key macros/constants include `__ASM_SH_KEXEC_H`, `KEXEC_SOURCE_MEMORY_LIMIT`, `KEXEC_DESTINATION_MEMORY_LIMIT`, `KEXEC_CONTROL_MEMORY_LIMIT`, `KEXEC_CONTROL_PAGE_SIZE`, `KEXEC_ARCH`. Structures include `pt_regs`. Functions or extern declarations include `reserve_crashkernel`.

## Control Flow
Control flow is mostly assembler/preprocessor expansion. The file emits instruction sequences, exception-table records, or linker-section metadata that become executable or discoverable at build time. Inline assembly and section directives mean compiler constraints, clobbers, branch-delay slots, and alignment are part of the interface.

## State And Persistence
State is encoded in generated sections, register save areas, and machine instructions rather than allocated here. Correctness depends on section names and offsets staying synchronized with linker and entry code.

## Dependencies And Integration Points
It directly depends on `asm/ptrace.h`, `asm/string.h`, `linux/kernel.h`. Kconfig-sensitive paths mention `CONFIG_KEXEC_CORE`. Integration points are assembler sources, linker script sections, generated offsets, and SH trap/entry code.

## Risks And Edge Cases
Risks are instruction-encoding, branch-delay, section-layout, and register-save mistakes. Small changes can cause boot, trap, or unwind failures that are hard to localize.

## Test Signals
Useful signals are assembler build coverage, objdump inspection of emitted sections, boot/trap smoke tests, unwind verification, and exception-table fixup tests.

Source read size: 72 lines, 2682 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/kexec.h -->
