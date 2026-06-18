# sources/distributed-fs/openafs/src/afs/afs_osi_alloc.c

## Purpose
`afs_osi_alloc.c` implements common OSI memory allocation helpers and the reusable small/large network buffer pools used by Rx and cache-manager code. It also updates memory-use statistics and performs pool cleanup at shutdown.

## Important APIs, types, and functions
Important globals are `osi_fsplock`, `osi_flplock`, `freePacketList`, `freeSmallList`, and the zero-length allocation sentinel `memZero`. General allocation APIs are `afs_osi_Alloc`, `afs_osi_Free`, and `afs_osi_FreeStr`. Pool APIs are `osi_AllocLargeSpace`, `osi_FreeLargeSpace`, `osi_AllocSmallSpace`, `osi_FreeSmallSpace`, and `shutdown_osinet`.

## Control flow
`afs_osi_Alloc` returns a non-null sentinel for zero-byte allocations, updates outstanding allocation counters, and calls Linux or generic kernel allocation. `afs_osi_Free` ignores null and the sentinel, updates counters, and frees through platform-specific APIs.

Large and small pool allocation first validate size against `AFS_LRALLOCSIZ` or `AFS_SMALLOCSIZ`. If no free-list item exists, they allocate a new fixed-size block and optionally pin it. Otherwise they pop a block under the corresponding lock. Freeing pushes a block back onto the free list under the lock and decrements active counters. `shutdown_osinet` drains both free lists, unpins where needed, reinitializes locks on cold shutdown, and warns if active block counts are nonzero.

## State and persistence behavior
All allocation state is runtime-only. The pool keeps only free fixed-size blocks; active blocks are tracked by counters but not by a list. Allocation statistics contribute to `afs_stats_cmperf`.

## Dependencies and integration points
The module depends on OSI allocation macros, Linux allocation wrappers, optional kernel pinning, AFS global-lock assertions, AFS locks, and stats. It is used heavily by ICL, Rx send/receive paths, fetch/store buffers, pioctl marshalling, UIO copies, and request allocation.

## Risks and edge cases
Pool free/alloc functions require the global lock on builds where `AFS_ASSERT_GLOCK` is meaningful. Size violations panic instead of returning errors. Active block leaks are only warned during shutdown. Zero-size allocation sentinel requires callers to free with the same size discipline but prevents false null allocation failures.

## Test signals
Test zero-byte allocation/free, large/small pool reuse, size-limit panics in debug builds, active counter accounting, shutdown warnings for leaked active blocks, pin/unpin coverage, and behavior when `AFS_PRIVATE_OSI_ALLOCSPACES` supplies private implementations.
