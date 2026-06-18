# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso2c.h

Purpose: template included by `vdso2c.c` to generate 32-bit and 64-bit ELF validation and C image emission logic.

Important APIs/functions: defines bitness-specific `go32()`/`go64()` through `BITSFUNC(go)`. It walks program headers, dynamic table, and section headers, validates a single load segment and no dynamic relocations, finds the symbol table, optionally writes raw stripped output, or emits a `struct vdso_image` C definition with aligned `raw_data`.

Control flow: it checks exactly one `PT_LOAD` at file offset and virtual address zero with equal file/memory size, records `PT_DYNAMIC`, rejects nonzero relocation sizes, requires `SHT_SYMTAB`, rounds stripped length to 8192-byte mapping size, and prints generated C.

State and persistence: writes build artifacts only. Generated `raw_data` is `__ro_after_init` and 8192-byte aligned for runtime mapping.

Dependencies and integration points: relies on `ELF_BITS`, `GET_BE`, `fail()`, and output stream state from `vdso2c.c`; produced C is consumed by `vma.c`.

Risks: validation protects runtime vDSO from unsupported relocation/layout shapes. Mapping-size rounding must match SPARC vDSO page size. Omitted dynamic symbols are intentional but section table presence is for debugger compatibility.

Test signals: run on valid 32/64 vDSOs, check generated `vdso_image` size/alignment, and confirm malformed ELF cases fail with clear errors.
