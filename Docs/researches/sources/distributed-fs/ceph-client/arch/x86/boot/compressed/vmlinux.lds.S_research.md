# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/vmlinux.lds.S

Purpose: linker script for the compressed kernel image. It defines entry points, layout, section ordering, alignment, page-table section placement, debug sections, and assertions that forbid runtime relocations/PLT/GOT surprises.

Important APIs and state: exports linker symbols such as `_head`, `_ehead`, `_text`, `_etext`, `_rodata`, `_erodata`, `_sbat`, `_esbat`, `_data`, `_edata`, `_bss`, `_ebss`, `_pgtable`, `_epgtable`, and `_end`. Entry is `startup_64` on x86-64 and `startup_32` on x86-32.

Control flow: build-time layout only. It places `.head.text` at address 0, compressed rodata, text/noinstr text, rodata, optional `.sbat`, page-aligned data, bss, optional x86-64 `.pgtable`, then aligns `_end` to a page. It discards dynamic and metadata sections and asserts `.got`, `.plt`, `.rel.dyn`, and `.rela.dyn` are empty.

Dependencies and integration: tightly coupled to compressed head assembly assumptions, EFI PE section metadata in `header.S`, SBAT inclusion, early BSS clearing, and page-table setup.

Risks and test signals: layout changes can break absolute assumptions in head code or EFI loaders. The assertions are important build-time tests for accidental compiler/linker features. Validate by building 32-bit/64-bit, EFI/SBAT variants, checking section addresses with `readelf`, and booting compressed images.
