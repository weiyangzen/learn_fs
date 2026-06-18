# sources/distributed-fs/ceph-client/arch/sparc/vdso/vma.c

Purpose: allocates, initializes, and maps SPARC vDSO and vvar pages into user processes.

Important APIs/functions/state: defines `vdso_enabled`, special mappings `vdso_mapping64` and `vdso_mapping32`, initcall `init_vdso()`, `init_vdso_image()`, `map_vdso()`, `arch_setup_additional_pages()`, and boot option parser `vdso_setup()`.

Control flow: `init_vdso()` copies built-in vDSO image bytes into freshly allocated pages and attaches them to special mappings. On exec, `arch_setup_additional_pages()` selects 64-bit or compat image, finds an unmapped area, optionally randomizes it, installs executable `[vdso]` text mapping after the vvar pages, maps vvar with `vdso_install_vvar_mapping()`, and records `mm->context.vdso`.

State and persistence: vDSO page arrays persist after init. Per-mm `context.vdso` records the user address. `vdso_enabled` is boot-option mutable.

Dependencies and integration points: depends on generated `vdso_image_*_builtin`, special mapping APIs, mmap locking, ASLR, vvar datapage constants, compat task detection, and ELF exec setup.

Risks: allocation failures disable vDSO globally. Mapping order and size must match vvar/vDSO page constants. Partial mapping failure must unmap text and clear `mm->context.vdso`.

Test signals: process exec with ASLR on/off, `vdso=0`, 64-bit and compat tasks, `/proc/<pid>/maps` `[vdso]` and vvar placement, GDB breakpoint COW behavior, and vDSO time selftests.
