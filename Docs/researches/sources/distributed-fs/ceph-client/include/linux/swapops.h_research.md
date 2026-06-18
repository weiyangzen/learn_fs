<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swapops.h -->
# sources/distributed-fs/ceph-client/include/linux/swapops.h

## Purpose

`swapops.h` defines architecture-independent manipulation of `swp_entry_t` values and conversion to page-table entries. It also builds special swap entries for device-private memory, migration, hardware poison, and PTE markers.

## Important APIs, types, and functions

Core macros are `SWP_TYPE_SHIFT`, `SWP_OFFSET_MASK`, `SWP_PFN_BITS`, `SWP_PFN_MASK`, migration A/D bit masks, and PTE marker bits. Functions include `pte_swp_clear_flags()`, `swp_entry()`, `swp_type()`, `swp_offset()`, `swp_entry_to_pte()`, radix/XArray conversions, device-private entry builders, migration entry builders and A/D marking, `migration_entry_wait*()`, `make_hwpoison_entry()`, `is_hwpoison_entry()`, `make_pte_marker_entry()`, `make_poisoned_swp_entry()`, `make_guard_swp_entry()`, THP PMD migration helpers, and `swp_entry_to_pmd()`.

## Control flow

VM code creates swap entries from type/offset, converts them into architecture PTE/PMD encodings, and later extracts type/offset for fault handling. Migration and device-private faults recognize special types and wait, migrate back, signal poison, or enforce userfault/guard semantics.

## State and persistence behavior

Swap entries persist inside page tables, swapcache XArrays, and shadow entries while mappings are absent. PTE markers intentionally persist metadata in otherwise-none PTE slots. No global state is owned here, except reading `swap_migration_ad_supported`.

## Dependencies and integration points

It depends on MMU builds, radix/XArray value storage, architecture `__swp_entry` conversion helpers, `swapfile.h`, migration, memory failure, device-private memory, userfaultfd write-protect, and THP migration.

## Risks and test signals

Risks include type/offset bit overlap, insufficient PFN bits, losing soft-dirty/UFFD/exclusive flags incorrectly, migration A/D encoding on unsupported architectures, and special entries escaping paths that expect real swap. Tests should cover encode/decode round trips, radix conversion, all special entry types, migration waits, PTE marker faults, THP migration stubs, and builds with `CONFIG_MMU`, `CONFIG_SWAP`, `CONFIG_MIGRATION`, and `CONFIG_MEMORY_FAILURE` toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swapops.h -->
