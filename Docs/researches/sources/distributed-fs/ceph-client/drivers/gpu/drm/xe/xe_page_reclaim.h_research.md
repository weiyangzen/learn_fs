
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_page_reclaim.h

## Purpose

`xe_page_reclaim.h` defines GuC page reclaim entry/list formats and declares helper APIs for page reclaim list lifecycle, submission backing storage, skip policy, and completion handling.

## Important APIs, Types, and Functions

- `struct xe_guc_page_reclaim_entry`: packed 64-bit GuC entry with valid bit, reclaim size order, and split physical address fields.
- `struct xe_page_reclaim_list`: CPU-side entries pointer and count, with invalid sentinel `XE_PAGE_RECLAIM_INVALID_LIST`.
- Inline helpers: `xe_page_reclaim_list_is_new()`, `xe_page_reclaim_list_valid()`, `xe_page_reclaim_entries_get()`, and `xe_page_reclaim_entries_put()`.
- Abort macro: `xe_page_reclaim_list_abort()` invalidates, increments a GT stat, and logs a debug reason.
- Declared functions for skip, BO creation, invalidation, init, allocation, and GuC done handling.

## Control Flow

Callers allocate/init a PRL, use inline validity checks while building reclaim requests, optionally abort with diagnostics, create a GuC-visible BO for submission, and release references when complete.

## State and Persistence Behavior

The header defines the PRL state machine: new is `{NULL, 0}`, valid is allocated/non-invalid, invalid uses a sentinel count. Entry storage lifetime is controlled by page refcounts.

## Dependencies and Integration Points

It depends on Linux bits/mm/slab/workqueue types and Xe GT/TLB/GUC/VMA forward declarations. Page-table and TLB invalidation code consume the format.

## Risks and Edge Cases

Because entries are packed bitfields in a raw `u64`, encoding mistakes can produce GuC-invisible or malformed reclaim requests. The abort macro evaluates `gt`/`prl` once but still assumes valid pointers.

## Test Signals

Bitfield encoding tests, validity-state tests, refcount tests, and abort-stat/log behavior should be covered.
