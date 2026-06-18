# sources/distributed-fs/ceph-client/arch/parisc/include/asm/bug.h

Purpose: provides PA-RISC implementations of `BUG()` and `WARN_ON()` using architecture break instructions and optional bug-table metadata.

Important APIs/types/functions: defines `HAVE_ARCH_BUG`, `HAVE_ARCH_WARN_ON`, `PARISC_BUG_BREAK_ASM`, `PARISC_BUG_BREAK_INSN`, `BUG()`, `__WARN_FLAGS`, and `WARN_ON()`.

Control flow: failing conditions emit a break instruction; with generic bug table support, metadata records file, line, flags, and condition string for diagnostics.

State and persistence: bug table entries persist in special ELF sections; runtime state is the trap frame produced by the break. Dependencies and integration: integrates with generic bug handling, exception decoding, and PA-RISC trap code.

Risks and test signals: wrong break encoding or table layout makes diagnostics misleading or prevents controlled panic/warn handling. Test with intentional WARN/BUG injection and objdump of bug-table sections.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
