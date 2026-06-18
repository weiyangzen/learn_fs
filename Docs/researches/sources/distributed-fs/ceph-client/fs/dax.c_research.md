# sources/distributed-fs/ceph-client/fs/dax.c

## Purpose
`dax.c` implements filesystem Direct Access support for persistent memory and other DAX devices. It manages DAX XArray entries, entry locking/waiting, page-fault insertion, direct read/write through iomap, writeback flushing, truncate/invalidate behavior, CoW/unshare, zeroing, dedupe compare, and layout-break handling for busy pinned pages.

## Important APIs, Types, and Functions
- Entry encoding helpers: `dax_make_entry()`, `dax_to_pfn()`, `dax_to_folio()`, `dax_entry_order()`, `dax_is_pmd_entry()`, `dax_is_zero_entry()`, and `dax_is_empty_entry()`.
- Locking/waiting: `dax_entry_waitqueue()`, `get_next_unlocked_entry()`, `wait_entry_unlocked_exclusive()`, `dax_lock_entry()`, `dax_unlock_entry()`, and `put_unlocked_entry()`.
- Folio association: `dax_folio_reset_order()`, `dax_associate_entry()`, `dax_disassociate_entry()`, `dax_busy_page()`, `dax_lock_folio()`, and `dax_lock_mapping_entry()`.
- Mapping lifecycle: `grab_mapping_entry()`, `dax_layout_busy_page_range()`, `dax_break_layout()`, `dax_break_layout_final()`, `dax_delete_mapping_entry()`, `dax_delete_mapping_range()`, and `dax_invalidate_mapping_entry_sync()`.
- I/O and persistence: `dax_iomap_rw()`, `dax_iomap_iter()`, `dax_zero_range()`, `dax_truncate_page()`, `dax_file_unshare()`, `dax_writeback_mapping_range()`, and `dax_writeback_one()`.
- Fault handling: `dax_iomap_fault()`, `dax_iomap_pte_fault()`, optional `dax_iomap_pmd_fault()`, `dax_fault_iter()`, `dax_finish_sync_fault()`, and zero-hole loaders.
- Range operations: `dax_dedupe_file_range_compare()` and `dax_remap_file_range_prep()`.

## Control Flow
For faults, callers enter `dax_iomap_fault()` with the required filesystem locks. PTE or PMD handlers grab a locked mapping entry, obtain iomap mappings, handle holes with zero pages, obtain PFNs with `dax_iomap_direct_access()`, insert or update the DAX entry, copy around shared CoW data if needed, and insert PTE/PMD mappings or return `VM_FAULT_NEEDDSYNC` for synchronous faults. Direct I/O uses `dax_iomap_rw()` and `iomap_iter()` to copy directly between iterators and DAX kernel addresses. Writeback tags dirty entries, write-protects mappings, flushes cache lines to persistence, and clears dirty/writeback tags under entry locks.

## State and Persistence
DAX state is stored as value entries in `mapping->i_pages`; bits encode lock state, PMD size, zero page, and empty placeholder entries. `mapping->nrpages` tracks page-equivalent coverage. DAX folios are associated with mappings and indices or marked shared via `folio->mapping == NULL` and `folio->share`. Persistent data lives on the DAX device and is made durable by `dax_flush()` and fsync paths; this file manages CPU cache persistence rather than page cache contents.

## Dependencies and Integration
The file depends on XArray, iomap, DAX device direct-access APIs, MM fault insertion helpers, reverse-map and VMA interval trees, writeback controls, page/folio internals, memory-failure/rmap expectations, block error translation, and tracepoints in `trace/events/fs_dax.h`. Filesystems integrate through iomap ops, DAX address spaces, truncate/punch/remap paths, mmap fault handlers, and fsync/writeback.

## Risks and Edge Cases
- XArray value entries overlap with internal error encodings, so fault errors are returned as XArray internal VM_FAULT entries rather than ERR_PTRs.
- PMD/PTE conflicts favor existing PTE entries; zero/empty PMD entries can be downgraded, while real PMD mappings are retained and dirtied.
- Entry lock waiting must account for inode teardown, stale `xa_state`, and PMD-aligned waitqueue keys.
- Shared/CoW mappings require invalidating existing entries and copying head/tail data to avoid exposing stale bytes.
- Synchronous `MAP_SYNC` faults defer PTE/PMD insertion until fsync completes.
- Busy pinned DAX pages must be unmapped and waited on before layout changes; NOWAIT callers receive `-ERESTARTSYS`.
- Hardware poison recovery uses `DAX_RECOVERY_WRITE` for writes after `-EHWPOISON`.
- Many paths assume page-size filesystem block granularity, especially writeback.

## Test Signals
Exercise DAX read/write through iomap, sparse-hole reads, mmap PTE and PMD faults, PMD fallback conditions, MAP_SYNC faults and `dax_finish_sync_fault()`, dirty writeback and flush ordering, truncate/punch invalidation, busy page detection with GUP pins, CoW/shared extent copy-around, zero/truncate-page behavior, unshare, dedupe compare, hardware-poison recovery writes, and lockdep/KCSAN coverage for XArray entry locking.
