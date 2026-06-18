# sources/distributed-fs/ceph-client/arch/s390/kernel/skey.c

Purpose: initializes storage keys for linker-registered memory regions that must be accessible from code running with a non-default access key.

Important APIs/functions/state: exports global `skey_regions_initialized`. `load_real_address()` uses the `lra` instruction to translate a virtual address to a real address. `__skey_regions_initialize()` iterates linker-defined `__skey_region_start` to `__skey_region_end`, sets each page's storage key to `PAGE_DEFAULT_KEY` with reference/change reset, and publishes completion.

Control flow: for every registered `struct skey_region`, the function rounds the start down to a page boundary, loops page by page until the region end, translates each page with `lra`, and calls `page_set_storage_key()`. A compiler barrier precedes `WRITE_ONCE(skey_regions_initialized, 1)` so observers do not see completion before key writes are ordered.

State and persistence: changes hardware storage-key metadata for registered real pages and sets a runtime completion flag. It is not filesystem persistence.

Dependencies and integration points: depends on linker-provided storage-key region tables, `asm/skey.h`, `PAGE_DEFAULT_KEY`, `page_set_storage_key()`, `lra`, and code paths that test `skey_regions_initialized` before running with non-default keys.

Risks: registered ranges must be valid mapped pages; `lra` on an invalid address would not produce the expected real address. The completion flag ordering matters for consumers that switch access keys. Every page in a region is modified, so incorrect region bounds can alter unrelated storage keys.

Test signals: boot/init paths that register skey regions should observe `skey_regions_initialized`, code using non-default access keys should access those regions successfully, and storage-key inspection should show `PAGE_DEFAULT_KEY` on each registered page.
