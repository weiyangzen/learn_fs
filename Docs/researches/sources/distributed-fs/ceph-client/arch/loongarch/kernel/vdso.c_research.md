# sources/distributed-fs/ceph-client/arch/loongarch/kernel/vdso.c

Purpose: initializes and maps the LoongArch vDSO image into user processes and tracks the per-mm vDSO base.

Important APIs, types, and functions: `vdso_info` is the global `struct loongarch_vdso_info`. `init_vdso()` allocates the page array for the linked vDSO image. `vdso_mremap()` updates `mm->context.vdso`. `vdso_base()` chooses a randomized base near `STACK_TOP`. The file also contains the architecture `arch_setup_additional_pages()` path, which maps `[vdso]` with `vm_special_mapping`.

Control flow: at `subsys_initcall`, the code verifies page alignment, records NUMA node IDs in `vdso_k_arch_data`, computes vDSO size, allocates `code_mapping.pages`, and maps each PFN from `vdso_start`. Per-process setup picks a randomized base when `PF_RANDOMIZE` is set, obtains `mmap_write_lock()`, uses `get_unmapped_area()`, calls `_install_special_mapping()`, and records the base in `mm->context.vdso`.

State and persistence: persistent kernel state is `vdso_info` and its allocated page array. Per-mm state is `mm->context.vdso`; per-CPU vDSO data gets node IDs. No on-disk state exists.

Dependencies and integration points: depends on generated vDSO offsets, the vDSO linker image, special mappings, randomization, ELF binfmt process setup, and vDSO data pages.

Risks: incorrect page alignment or size calculation breaks process startup mappings. Randomization must still leave a valid unmapped area. `vdso_mremap()` must keep `mm->context.vdso` accurate after remap.

Test signals: process startup, `getauxval(AT_SYSINFO_EHDR)`, vDSO symbol calls such as time functions, ASLR variance, mremap behavior, and page table inspection for `[vdso]`.
