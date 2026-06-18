# sources/distributed-fs/ceph-client/arch/x86/mm/pat/set_memory.c

## Purpose
`set_memory.c` implements x86 change-page-attribute (CPA) operations for kernel mappings. It changes cacheability, execute/write/present/global/encryption bits, keeps direct-map and high-kernel-map aliases coherent, splits and collapses large mappings when required, and provides the exported `set_memory_*()` and `set_pages_*()` APIs used by drivers, debug page allocation, memory failure recovery, confidential-computing guests, EFI mapping setup, and vmalloc/ioremap users.

## Important APIs, Types, and Functions
The central state object is `struct cpa_data`, which carries the target address or page array, optional alternate `pgd`, masks to set and clear, current PFN/page cursor, flags such as `CPA_ARRAY`, `CPA_PAGES_ARRAY`, `CPA_NO_CHECK_ALIAS`, and `CPA_COLLAPSE`, and split/flush controls. Public APIs include `lookup_address()`, `lookup_address_in_pgd()`, `lookup_pmd_address()`, `slow_virt_to_phys()`, `clflush_cache_range()`, `set_memory_uc/wc/wb/x/nx/ro/rox/rw/np/p/4k/nonglobal/global()`, `set_mce_nospec()`, `clear_mce_nospec()`, `set_memory_encrypted()`, `set_memory_decrypted()`, `set_pages_*()`, direct-map noflush helpers, `kernel_page_present()`, and boot-only `kernel_map_pages_in_pgd()`/`kernel_unmap_pages_in_pgd()`.

## Control Flow and State
Callers enter through `change_page_attr_set_clr()`, which canonicalizes unsupported protection bits, aligns inputs, flushes highmem/vmalloc aliases, fills `cpa_data`, and delegates to `__change_page_attr_set_clr()`. The inner loop resolves each current target with `_lookup_address_cpa()`, handles absent entries through `__cpa_process_fault()`, updates 4K PTEs directly, or calls `should_split_large_page()` to preserve, split, or rewrite large pages. Static protection enforcement prevents unsafe changes to executable kernel text, read-only rodata, and PCI BIOS ranges. Alias processing updates the direct map and, on x86-64, the high kernel text/data mapping for the same PFN. If any entry changed, `cpa_flush()` selects all-CPU TLB flushes, single-page flushes, cache writeback/invalidation, and optional large-page collapse.

## State and Persistence
Persistent kernel state includes direct-map page-size counters exposed in `/proc/meminfo`, optional CPA debugfs counters, memtype reservations for UC/WC/WB transitions, `mem_enc_lock` serialization for private/shared memory conversion, global PGD synchronization through `pgd_lock`/`pgd_list`, and page-table pages allocated or freed by split/collapse paths. Hardware-visible state is the page-table tree, TLB contents, CPU caches, and guest encryption attribute notifications.

## Dependencies and Integration Points
This file depends on PAT/memtype tracking, x86 page-table helpers, TLB flush primitives, highmem and vmalloc alias management, debugfs/procfs, memblock/E820, paravirt page-table hooks, confidential-computing platform callbacks, MCE poison-page recovery, debug page allocation, and KVM/EFI callers that need alternate PGDs or exact physical translation behavior.

## Risks and Test Signals
Risks are concentrated around stale large-page TLB entries during split/collapse, alias mismatches between direct map and high map, static-protection bypasses, incorrect cache-mode reservation rollback, non-canonical MCE decoy addresses, and conversion races between encrypted and decrypted memory. Test signals include CPA debugfs counter movement, direct-map size accounting, W^X warnings, successful module/vmalloc/ioremap cache-mode transitions, MCE poison isolation, debug-pagealloc present-bit toggling, EFI boot mappings before SMP, and confidential-guest shared/private conversion tests.
