<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/grant_table.h -->
# sources/distributed-fs/ceph-client/include/xen/grant_table.h

## Purpose
This header declares Linux Xen grant-table APIs for granting foreign domains access to local pages, mapping foreign grants, managing grant references, allocating grant pages, DMA grant allocation, batching map/copy operations, and iterating grant-sized chunks.

## Important APIs, Types, And Functions
- `INVALID_GRANT_REF`, `INVALID_GRANT_HANDLE`, and `NR_GRANT_FRAMES` define sentinel and initial shared-table sizing.
- `struct gnttab_free_callback` schedules callbacks when free grant references become available.
- `struct gntab_unmap_queue_data` describes asynchronous unmap work, callbacks, map arrays, pages, count, and age.
- Lifecycle APIs include `gnttab_init()`, optional suspend/resume, grant foreign access, ending/trying to end access, and freeing pages after access ends.
- Reference-pool APIs allocate, claim, release, free, and callback-wait for grant references or sequences.
- Mapping helpers `gnttab_set_map_op()` and `gnttab_set_unmap_op()` prepare ABI operations with PV/HVM host address differences.
- Architecture hooks map shared/status frames and auto-xlat frames.
- Page APIs allocate/free pages, manage page caches, mark grant pages private, map/unmap refs sync or async, and batch map/copy with retry of `GNTST_eagain`.
- `struct xen_page_foreign` stores foreign page origin in `page->private`.
- Iteration helpers split arbitrary page ranges into Xen page-sized grant chunks and count grants with `gnttab_count_grant()`.

## Control Flow
Granting flow allocates or claims references, grants a frame to a domain, hands out the ref, and later ends access only when the peer is no longer using it. Mapping flow builds map ops, performs hypercalls, sets foreign P2M mappings, uses returned handles/addresses, then unmaps synchronously or queues async unmap work. Batch operations retry transient paged-out grants until statuses settle.

## State And Persistence
Persistent state includes grant reference pools, shared/status grant tables, free callbacks, page caches, auto-xlat frames, page-private foreign metadata, asynchronous unmap queues, and hypervisor grant entries. Foreign access can outlive the API call until the remote domain releases it.

## Dependencies And Integration Points
It depends on Xen public grant ABI, Xen features/page helpers, architecture hypervisor/page mapping, Linux page flags, delayed work, spinlocks, DMA types, and optional grant DMA allocation. It integrates with Xenbus front/back drivers, net/block grants, balloon/unpopulated pages, DMA, and suspend/resume.

## Risks And Edge Cases
`gnttab_end_foreign_access()` may return before the peer stops accessing the page; pages cannot be reused until final release. Host address preparation differs for `GNTMAP_contains_pte`, PV, and HVM. Linux pages may contain multiple Xen grant chunks. Batch retry can wait up to about 32 seconds, so callers must account for latency. `page->private` storage differs by word size.

## Test Signals
Signals include correct grant allocation/free accounting, successful foreign access and revocation, map/unmap of local and foreign refs, async unmap callback completion, no page reuse while grants are active, batch retry handling for `GNTST_eagain`, correct grant counts for unaligned ranges, and suspend/resume restoration of shared tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/grant_table.h -->
