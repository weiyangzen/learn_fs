# sources/distributed-fs/ceph-client/include/linux/migrate.h

## Purpose
Exposes MM page/folio migration APIs, driver movable-page callbacks, CONFIG-gated stubs, NUMA balancing hooks, and device-private/device-coherent VMA migration helpers.

## Important APIs/Types
Defines `new_folio_t`, `free_folio_t`, `struct movable_operations`, and `migrate_reason_names`. Under `CONFIG_MIGRATION`, APIs include `putback_movable_pages`, `migrate_folio`, `migrate_pages`, `alloc_migration_target`, isolation helpers, huge-page mapping migration, `softleaf_entry_wait_on_locked`, folio flag/mapping migration, and `set_movable_ops`. It also defines `MIGRATE_PFN_*` flags, `migrate_pfn_to_page`, `migrate_pfn`, `enum migrate_vma_direction`, `struct migrate_vma`, and device migration setup/pages/finalize helpers.

## Control Flow
Migration isolates pages, allocates target folios, migrates mappings/flags/content, then frees old pages or puts failures back. Movable driver pages follow isolate, migrate, and putback callbacks. Device VMA migration follows setup, caller destination allocation/population, page migration, and finalize.

## State And Persistence
Migration changes page mappings, folio flags, PFN arrays, and device/system memory residency. `migrate_vma` state must persist unchanged across setup/pages/finalize.

## Dependencies And Integration Points
Depends on MM, mempolicy, hugetlb, and migration mode definitions. Integrates with compaction, hotplug, memory failure, NUMA balancing, HMM/device memory, GPU drivers, filesystems/address spaces, and DAMON.

## Risks
Touching `page->lru` incorrectly, blocking in async mode, stale PFN flags, missed putback, pinned pages, MMU notifier ordering mistakes, and assuming disabled-config stubs do real work.

## Test Signals
Compaction, hotplug, memory-failure, NUMA, huge-page, movable-page, and HMM migration tests; fault injection for retry/permanent errors; CONFIG_MIGRATION=n builds; and lockdep/MMU notifier checks.
