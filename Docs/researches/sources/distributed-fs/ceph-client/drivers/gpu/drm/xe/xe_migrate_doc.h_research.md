
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_migrate_doc.h

## Purpose

`xe_migrate_doc.h` is documentation-only kernel-doc for the Xe migrate layer. It explains why the driver creates a special per-GT migration VM and how generated jobs use that VM for copy, clear, and page-table bind work.

## Important APIs, Types, and Functions

The file exports no C symbols. Its `DOC: Migrate Layer` block documents the migration VM layout, bind job structure, copy/clear job structure, limits from reserved page-table pages, and future work items.

## Control Flow

The documented flow is two-stage for both bind and copy/clear jobs: first update the migration VM page structure to point at target BOs or page-table BOs, then execute the actual PTE programming, copy, or clear after a ring-side TLB invalidation boundary. Large BO operations are split into multiple jobs.

## State and Persistence Behavior

The documentation states that the migration VM has reserved physical pages for BO mappings, a kernel bind page, user bind pages managed by `drm_suballoc`, and identity-mapped VRAM. User bind suballocations return to the pool after job completion; kernel bind pages are serially reused.

## Dependencies and Integration Points

This file is consumed by generated kernel documentation and complements `xe_migrate.c`/`xe_migrate.h`. It also explains constraints visible to VM bind, BO eviction, and clear/copy callers.

## Risks and Edge Cases

The document contains TODO/future-work notes around diagrams, using identity-mapped VRAM for copy/clear, better async bind page utilization, large pages for sysmem, and possible sysmem identity mapping. These are signs that implementation details may evolve and documentation should be kept synchronized.

## Test Signals

Documentation validation is mostly build-doc coverage. Functional tests should compare documented max copy/clear sizes and two-batch/TLB invalidation expectations against migration implementation behavior.
