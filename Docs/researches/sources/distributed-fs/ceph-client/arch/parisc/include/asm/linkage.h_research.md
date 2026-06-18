# sources/distributed-fs/ceph-client/arch/parisc/include/asm/linkage.h

Purpose: provides PA-RISC linkage and symbol annotation macros for assembly/C ABI boundaries.

Important APIs/types/functions: defines architecture-specific `ENTRY`, `END`, alignment, and calling-convention annotations layered on generic linkage.

Control flow: assembly files use these macros to expose functions with correct symbol type, alignment, and unwind/linker metadata.

State and persistence: no runtime state; affects ELF symbol table and code layout. Dependencies and integration: used by boot, syscall, trap, and library assembly routines.

Risks and test signals: bad linkage annotations break kallsyms, ftrace, unwinding, or module relocation. Test through objdump/readelf symbol inspection and all assembly builds.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
