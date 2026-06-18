# sources/distributed-fs/ceph-client/mm/mapping_dirty_helpers.c

## Purpose

`mapping_dirty_helpers.c` provides exported helpers for write-protecting and dirty-bit harvesting over all VMAs that map a shared `address_space` range. It supports filesystem/device dirty tracking use cases that need to protect PTEs, clean dirty PTEs, and record exactly which page offsets were dirty.

## Important APIs, types, and functions

The exported APIs are `wp_shared_mapping_range()` and `clean_record_shared_mapping_range()`. Internal walk state is `struct wp_walk`, which stores an MMU notifier range, the minimal TLB flush subrange, and a modified-PTE count. `struct clean_walk` extends it with a page-offset bitmap, bitmap base offset, and first/last touched bit range.

Pagewalk callbacks are `wp_pte()` for write-protecting PTEs, `clean_record_pte()` for cleaning dirty PTEs and recording offsets, `wp_clean_pmd_entry()` and `wp_clean_pud_entry()` for huge-entry handling, `wp_clean_pre_vma()` for notifier/cache/TLB setup, `wp_clean_post_vma()` for TLB flush and notifier completion, and `wp_clean_test_walk()` for VMA filtering.

## Control flow

Both exported helpers take `i_mmap_lock_read(mapping)`, call `walk_page_mapping()` across `first_index..first_index + nr`, and release the mapping lock. `wp_shared_mapping_range()` uses `wp_walk_ops`; for each applicable PTE, `wp_pte()` converts writable PTEs to read-only with `ptep_modify_prot_start()`/`commit()`, counts them, and expands the flush subrange.

`clean_record_shared_mapping_range()` uses `clean_walk_ops`; `clean_record_pte()` checks dirty PTEs, computes the address-space page offset from VMA start and `vm_pgoff`, cleans the PTE, records the corresponding bitmap bit, updates the touched bit interval, and counts the cleaned PTE. Pre/post VMA callbacks wrap each VMA walk in MMU notifier invalidation, cache flushing, and pending TLB-flush accounting. If nested TLB flushes are pending, the post callback flushes the full notifier range; otherwise it flushes only the modified subrange.

## State and persistence behavior

Persistent effects are page-table changes in processes mapping the address space: writable PTEs become write-protected and dirty PTEs become clean. `clean_record_shared_mapping_range()` also mutates the caller-provided bitmap and `start`/`end` output range. The helpers do not store state after returning. They explicitly warn but skip transparent huge PMD/PUD entries to avoid dirty information loss from splitting huge mappings in this helper path.

## Dependencies and integration points

The file depends on reverse mapping through `walk_page_mapping()`, `i_mmap_lock_read()`, pagewalk callbacks, VMA flags, MMU notifier APIs, architecture cache/TLB flush APIs, PTE modification primitives, and bit operations. `wp_clean_test_walk()` limits work to shared, may-write, non-hugetlb VMAs, so private/COW, read-only, PFN-only by exclusion, and hugetlb mappings are not dirty-tracked here.

## Risks and edge cases

The dirty-recording guarantees are race-aware but not exclusive: PTEs dirtied after the walk begins may remain dirty, be recorded, or both. Callers needing a closed dirty snapshot must first write-protect the range and block new writers in `page_mkwrite()`/`pfn_mkwrite()`, then harvest after the TLB flush. Bitmap bounds are caller-owned: `bitmap_pgoff` and allocation must cover the walked range. Huge PMD/PUD entries are skipped with warnings if dirty/write-enabled, so callers must account for that limitation. Correct notifier and TLB ordering is required for secondary MMUs and CPUs to observe protection/dirty-bit transitions.

## Test signals

Tests should map a shared file into multiple processes, dirty selected offsets, call `clean_record_shared_mapping_range()`, and verify bitmap bits and start/end compaction. Write-protect tests should confirm later writes fault through the filesystem/device write path and that already read-only PTEs are not counted. Stress should include concurrent writers, nested TLB flush conditions, secondary MMU notifier consumers, non-applicable VMAs, huge PMD/PUD mappings, empty ranges, and bitmap base offsets that do not equal `first_index`.
