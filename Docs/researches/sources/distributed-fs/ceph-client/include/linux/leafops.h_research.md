# sources/distributed-fs/ceph-client/include/linux/leafops.h

Purpose: defines a software abstraction for non-present page-table leaf entries (`softleaf_t`) so swap, migration, device-private, device-exclusive, hardware-poison, and marker entries can be inspected without open-coding architecture PTE/PMD encodings.

Important APIs and types: `enum softleaf_type` classifies entry families. Conversion helpers include `softleaf_from_pte()`, `softleaf_to_pte()`, and, with THP migration support, `softleaf_from_pmd()`. Predicate helpers identify swap, migration variants, device private/exclusive, hwpoison, markers, poison/guard/UFFD-WP markers, PMD device-private, and PMD migration entries. `softleaf_to_marker()`, `softleaf_has_pfn()`, `softleaf_to_pfn()`, `softleaf_to_page()`, `softleaf_to_folio()`, and migration A/D-bit helpers expose encoded data.

Control flow: MM code converts a non-present PTE/PMD to `softleaf_t`, classifies it, and then branches to swap, migration, device-memory, hwpoison, or userfaultfd marker handling. Migration PFN access enforces a read barrier and warns if the referenced folio is not locked.

State and persistence: no independent state is stored. The abstraction mirrors encoded page-table state and swap-entry metadata; persistence follows page tables and swap/device migration state.

Dependencies and integration points: depends on `mm_types.h`, `swapops.h`, swap constants, migration/device/private-memory configs, folio helpers, and architecture conversion helpers. It is a central MM integration point for page fault, migration, userfaultfd, and zone-device code.

Risks and test signals: risks include type-number drift with swap encodings, losing soft-dirty/UFFD flags during conversion, accepting invalid PMD entries, PFN extraction width bugs, and migration locking violations. Test with swap, THP migration, device-private memory, hwpoison, UFFD poison/WP markers, guard markers, and config matrices with features disabled.
