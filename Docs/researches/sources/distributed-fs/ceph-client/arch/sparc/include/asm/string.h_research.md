# sources/distributed-fs/ceph-client/arch/sparc/include/asm/string.h

Purpose: SPARC architecture header `string.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: functions/helpers `memcmp`, `strlen`, `strncmp`; macros/constants `___ASM_SPARC_STRING_H`, `__HAVE_ARCH_MEMMOVE`, `__HAVE_ARCH_MEMCPY`, `memcpy`, `__HAVE_ARCH_MEMSET`, `memset`, `__HAVE_ARCH_MEMSCAN`, `memscan`, `__HAVE_ARCH_MEMCMP`, `__HAVE_ARCH_STRLEN`, `__HAVE_ARCH_STRNCMP`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_STRING_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `asm/string_64.h`, `asm/string_32.h`. Integration points include memory-management; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
