# sources/distributed-fs/ceph-client/arch/arm64/mm/pageattr.c

## Purpose
This file implements ARM64 runtime page-attribute changes for vmalloc mappings, direct-map validity changes, and Realm memory encryption/decryption transitions. It walks kernel page tables, updates PTE/PMD/PUD attributes, splits large mappings when necessary, and flushes TLBs when valid cached translations may exist.

## Important APIs, Types, and Functions
The main exported behavior is through `set_memory_ro()`, `set_memory_rw()`, `set_memory_nx()`, `set_memory_x()`, `set_memory_valid()`, `set_direct_map_invalid_noflush()`, `set_direct_map_default_noflush()`, `set_direct_map_valid_noflush()`, `__kernel_map_pages()` under `CONFIG_DEBUG_PAGEALLOC`, `kernel_page_present()`, and `realm_register_memory_enc_ops()`.

Important helpers and types include `struct page_change_data`, `set_pageattr_masks()`, `pageattr_pud_entry()`, `pageattr_pmd_entry()`, `pageattr_pte_entry()`, `pageattr_ops`, `rodata_full`, `can_set_direct_map()`, `update_range_prot()`, `__change_memory_common()`, `change_memory_common()`, and `__set_memory_enc_dec()`.

## Control Flow
The page-table walk callbacks update leaf entries by clearing `clear_mask` first and then setting `set_mask`, because some bits alias each other. `update_range_prot()` first calls `split_kernel_leaf_mapping()` for the range, then walks kernel page tables under lazy MMU mode. `__change_memory_common()` wraps this and flushes the TLB unless the transition is only present-invalid to valid.

`change_memory_common()` validates that the requested range is page-aligned and fully covered by one vmalloc/vmap area with `VM_ALLOC` and without `VM_ALLOW_HUGE_VMAP`. For read-only changes under `rodata_full`, it also applies the same permission update to each backing page's linear-map alias. It flushes lazy vmalloc aliases before updating the vmalloc mapping itself.

Direct-map helpers use `can_set_direct_map()` to no-op unless the platform requires page-granular direct-map control. Realm encryption/decryption uses `__set_memory_enc_dec()`: it requires Realm world and a linear-map address, invalidates the mapping while setting or clearing `PROT_NS_SHARED`, calls RSI to change protected/shared state, then makes the mapping valid again. Realm failures warn that pages may be leaked.

## State and Persistence
`rodata_full` is a boot-time policy flag that affects whether backing linear-map aliases are updated alongside vmalloc mappings. Page-table entries themselves persist the changed protections. Realm transitions persist both in page-table attributes (`PROT_NS_SHARED`, valid/invalid state) and in external Realm state managed through RSI calls.

## Dependencies and Integration Points
This file depends on the `mmu.c` split and walk infrastructure, generic vmalloc metadata, cache/TLB flush helpers, mem_encrypt dispatcher, KFENCE, debug pagealloc, Realm services (`rsi_set_memory_range_*()`), and page-table bit definitions. It registers Realm memory encryption ops with `arm64_mem_crypt_ops_register()`.

## Risks
Changing attributes on live kernel mappings is unsafe unless the range is already page-granular or can be split safely. The vmalloc area checks intentionally reject huge vmaps to avoid splitting live section mappings. Missing linear-map alias updates under `rodata_full` could leave writable aliases of read-only text/data. Realm transitions intentionally invalidate mappings before RSI calls; failures can force callers to leak memory to avoid unsafe reuse.

## Test Signals
Useful tests include module text permission changes, BPF executable memory transitions, debug pagealloc direct-map invalidation, KFENCE pool behavior, rodata alias checks, Realm shared/protected memory conversion tests, and `kernel_page_present()` checks. TLB flush issues may appear as stale executable/write permissions or data aborts after validity toggles.
