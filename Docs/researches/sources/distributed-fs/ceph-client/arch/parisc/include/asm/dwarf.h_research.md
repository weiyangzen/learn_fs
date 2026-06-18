# sources/distributed-fs/ceph-client/arch/parisc/include/asm/dwarf.h

Purpose: defines PA-RISC DWARF register numbering and unwind-related constants for debugging/unwinding integration.

Important APIs/types/functions: exports architecture register number mappings used by unwinders, debug info, and low-level assembly annotations.

Control flow: unwinder/debug tooling uses these constants to map saved machine registers to DWARF register slots.

State and persistence: no runtime state; the mappings become part of generated debug/unwind metadata. Dependencies and integration: used by stack unwinding, ftrace/debug code, and toolchain-facing assembly.

Risks and test signals: wrong register numbers produce misleading traces. Test with kernel stack unwinding, kgdb backtraces, and objdump/readelf inspection of CFI where present.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
