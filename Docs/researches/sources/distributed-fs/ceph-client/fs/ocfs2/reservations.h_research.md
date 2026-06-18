# sources/distributed-fs/ceph-client/fs/ocfs2/reservations.h

## Purpose
`reservations.h` defines the public reservation-window data structures and APIs used by OCFS2 allocation code to reserve ranges in allocation bitmaps.

## Important APIs, types, and functions
The header defines reservation level bounds (`OCFS2_DEFAULT_RESV_LEVEL`, `OCFS2_MAX_RESV_LEVEL`, `OCFS2_MIN_RESV_LEVEL`), `struct ocfs2_alloc_reservation`, flags `OCFS2_RESV_FLAG_INUSE`, `OCFS2_RESV_FLAG_TMP`, and `OCFS2_RESV_FLAG_DIR`, and `struct ocfs2_reservation_map`. The API covers initialization, type assignment, directory-reservation eligibility, discard, map init/restart/uninit, lookup of reservable bits, and notification that bits were claimed.

## Control flow
Allocators embed or allocate `ocfs2_alloc_reservation`, initialize it once, optionally set temporary or directory type flags, then call `ocfs2_resmap_resv_bits` to receive a candidate start/length. Once the allocator actually claims bits in the disk bitmap, it calls `ocfs2_resmap_claimed_bits` so the reservation can be shortened or moved in LRU order. When the allocation context ends or the bitmap changes, callers discard or restart reservations.

## State and persistence
The structures are runtime-only. A reservation map points at a disk bitmap buffer and records the bitmap length, but the reservation windows themselves are not written to disk. `r_last_start` and `r_last_len` guide future placement after successful allocations.

## Dependencies and integration points
The header depends on Linux rbtrees and OCFS2 superblock definitions. It is consumed by allocator code that owns local allocation windows and by inode allocation contexts that want locality hints.

## Risks and test signals
Risks include misuse of flags outside `OCFS2_RESV_TYPES`, calling claimed-bits with a start different from the reservation start, failing to discard reservations when allocator state is destroyed, and stale disk bitmap pointers after local alloc slides. Test signals are allocation tests with reservations disabled/enabled, temporary reservation one-shot behavior, directory reservations, map restart coverage, and lockdep/KASAN around reservation lifetime.
