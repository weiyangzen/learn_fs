
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_page_reclaim.c

## Purpose

`xe_page_reclaim.c` implements helper logic for GuC page reclaim lists, which extend TLB invalidation with page-reclaim/PPC flush work for VM unbind or invalidation flows.

## Important APIs, Types, and Functions

- `xe_page_reclaim_skip()` decides whether a VMA needs page reclaim based on null VMA and PAT L3 policy.
- `xe_page_reclaim_create_prl_bo()` suballocates a GGTT reclaim-pool BO, copies PRL entries, flushes CPU writes, and schedules BO release on a TLB invalidation fence.
- `xe_page_reclaim_list_invalidate()`, `xe_page_reclaim_list_init()`, and `xe_page_reclaim_list_alloc_entries()` manage CPU-side PRL entry storage.
- `xe_guc_page_reclaim_done_handler()` delegates completion messages to the TLB invalidation done handler.

## Control Flow

Callers initialize or allocate a PRL, populate entries elsewhere, skip unnecessary VMAs, then create a reclaim BO when submitting the GuC request. The BO contains entries plus a terminating null entry and is freed when the paired invalidation fence signals. Completion handling follows the same seqno/fence logic as TLB invalidation.

## State and Persistence Behavior

CPU PRL entries live in one allocated page with refcount helpers. A PRL can be invalidated by setting entries to NULL and `num_entries` to `XE_PAGE_RECLAIM_INVALID_LIST`. Reclaim BO suballocations persist only until the associated fence completes.

## Dependencies and Integration Points

The file depends on PAT policy lookup, tile reclaim pools, Xe SA BO helpers, GuC TLB invalidation fence/message code, and GT stats/logging via the header abort macro.

## Risks and Edge Cases

- PRL size is capped at one 4 KiB page and 512 entries; overpopulation must be prevented by callers.
- Atomic allocation is used for reclaim BO creation, so reclaim-pool pressure can fail late.
- `xe_page_reclaim_skip()` assumes transient display policy is safely flushed by hardware sequencing.
- Invalidation drops the backing page ref; callers must not use entries after invalidating.

## Test Signals

Tests should cover skip policy for null/transient-display/other PAT VMAs, PRL allocation/invalidation refcounts, reclaim BO contents including terminator, fence-based suballoc freeing, and malformed GuC completion handling through the delegated TLB path.
