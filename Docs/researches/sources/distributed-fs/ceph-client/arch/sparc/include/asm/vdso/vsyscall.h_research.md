# sources/distributed-fs/ceph-client/arch/sparc/include/asm/vdso/vsyscall.h

Purpose: SPARC VDSO vsyscall glue that includes generic VDSO vsyscall support and declares the architecture VDSO mapping size with `__VDSO_PAGES`.

Important APIs/types/functions: macros/constants `_ASM_SPARC_VDSO_VSYSCALL_H`, `__VDSO_PAGES`.

Control flow: The file is declarative; generic VDSO build/runtime code consumes `__VDSO_PAGES` while syscall fallback logic lives in `vdso/gettimeofday.h` and the generic include.

State and persistence behavior: It owns no mutable state. The page-count constant becomes part of the persistent VDSO image/mapping contract used when the kernel maps VDSO pages into user processes.

Dependencies and integration points: Includes/dependencies: `asm-generic/vdso/vsyscall.h`. Integration points include VDSO image layout, process `mmap`/exec setup, and generic VDSO symbol handling.

Risks and test signals: Main risks are an incorrect VDSO page count causing truncated or overlarge mappings, mismatch with `vdso_image`, and build drift from generic VDSO APIs. Test signals include VDSO image size checks, exec-time VDSO mapping tests, symbol resolution from user space, and sparc32/sparc64 VDSO builds.
