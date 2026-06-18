<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/vdso2c.h -->
# sources/distributed-fs/ceph-client/arch/x86/tools/vdso2c.h

## Purpose
`vdso2c.h` is a macro-parametric implementation included twice by `vdso2c.c` to generate 32-bit and 64-bit vDSO conversion routines.

## Important APIs, types, and functions
It defines `BITSFUNC(copy)`, `BITSFUNC(extract)`, and `BITSFUNC(go)`. The generated `go32()`/`go64()` parse ELF headers, program headers, dynamic tags, section headers, symbol tables, altinstructions, and exception tables.

## Control flow
The converter verifies a single load segment at offset/vaddr zero, rejects dynamic relocations, locates required symbols, optionally writes raw stripped output, otherwise emits a page-aligned `raw_data` array and `struct vdso_image` with symbol offsets and optional alt/extable metadata.

## State and persistence behavior
State is local parsing variables and collected signed-width symbol offsets. Persistent state is generated C arrays and image metadata.

## Dependencies and integration points
It depends on `ELF_BITS` macros, little-endian access helpers, `required_syms[]`, and vDSO linker scripts producing the expected ET_DYN shape.

## Risks and edge cases
Malformed section offsets can overrun input; the code explicitly checks extracted sections. Missing symbols or dynamic relocations fail hard because runtime vDSO mapping cannot fix them.

## Test signals
Signals are generated C compilation, vDSO initcall success, symbol-offset validation, and userland `clock_gettime`/signal trampoline behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/tools/vdso2c.h -->
