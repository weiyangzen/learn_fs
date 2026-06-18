# sources/distributed-fs/ceph-client/arch/mips/mm/page-funcs.S

Purpose: reserves executable code slots for runtime-generated `clear_page` and `copy_page` implementations.

Important symbols: exports `__clear_page_start`, `__clear_page_end`, `__copy_page_start`, and `__copy_page_end`. Defines either `clear_page`/`copy_page` directly or CPU fallback names `clear_page_cpu`/`copy_page_cpu` under `CONFIG_SIBYTE_DMA_PAGEOPS`.

Control flow: initial functions are dummy infinite jumps followed by fixed `.space` areas. `page.c` overwrites these slots at boot using the uasm generator, then callers execute the generated code.

State and persistence: the reserved text area is patched once at boot and then acts as kernel text. Function symbols are exported.

Dependencies and integration: paired with `build_clear_page()` and `build_copy_page()` in `page.c`; size comments define maximum generated sequence budgets.

Risks and test signals: generated code must fit the reserved spaces. Test boot-time `BUG_ON(buf > end)` never triggers, symbols export correctly, and generated clear/copy work under all selected CPU/cache configurations.
