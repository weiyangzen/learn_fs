# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-const.h

Purpose: provides constants that can be shared between assembler and C contexts without type suffix problems.

Important APIs/types/functions: includes `<vdso/const.h>` and depends on the VDSO `ASM_CONST`/constant helpers for architecture headers that need constants in both C and assembly.

Control flow: declarative include wrapper only.

State and persistence: no runtime state.

Dependencies and integration points: many PowerPC MMU, barrier, bit, and instruction headers include this before defining large constants used in assembly or inline asm.

Risks: if the included VDSO constant interface changes, architecture headers using `ASM_CONST` can break in assembly-only builds. Because this file is tiny, accidental removal can produce widespread compile errors.

Test signals: compile C and assembler translation units that include Book3S MMU headers, especially constants above 32 bits.
