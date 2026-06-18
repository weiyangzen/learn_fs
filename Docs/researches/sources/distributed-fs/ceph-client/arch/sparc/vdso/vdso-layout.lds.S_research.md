# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso-layout.lds.S

Purpose: defines the common ELF section and program-header layout for SPARC vDSO images.

Important APIs/sections: emits vvar symbols with `VDSO_VVAR_SYMS`, then lays out hash, dynamic symbol/string/version sections, dynamic table, read-only data, notes, unwind frames, and text. Defines PHDRs for one read/execute `PT_LOAD`, read-only `PT_DYNAMIC`, `PT_NOTE`, and GNU EH frame header.

Control flow: this is a linker script include used by both 64-bit and 32-bit vDSO scripts. It discards bug/discard sections and fills text padding with `0x90909090`.

State and persistence: build-time layout only; controls in-memory vDSO segment shape.

Dependencies and integration points: included by `vdso.lds.S` and `vdso32.lds.S`; depends on vDSO datapage/page headers and SPARC vvar/vsyscall constants.

Risks: vDSO requires a single load segment with no dangling non-allocatable runtime content. Wrong PHDR flags, page size, or vvar placement breaks mapping or userspace dynamic tools.

Test signals: `readelf -lS` should show one PT_LOAD, read-only data/text layout, notes/build-id, unwind sections, exported vvar symbols, and no unexpected writable segment.
