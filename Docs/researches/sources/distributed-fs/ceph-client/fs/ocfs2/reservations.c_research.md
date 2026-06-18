# sources/distributed-fs/ceph-client/fs/ocfs2/reservations.c

## Purpose
`reservations.c` implements allocation reservation windows for OCFS2 bitmap allocators. Reservations give inodes or temporary callers a preferred contiguous range of free bits in a local allocation bitmap, improving locality and reducing repeated bitmap searches.

## Important APIs, types, and functions
The public API includes `ocfs2_dir_resv_allowed`, `ocfs2_resv_init_once`, `ocfs2_resv_set_type`, `ocfs2_resmap_init`, `ocfs2_resv_discard`, `ocfs2_resmap_restart`, `ocfs2_resmap_uninit`, `ocfs2_resmap_resv_bits`, and `ocfs2_resmap_claimed_bits`. Internal helpers manage rb-tree insertion/removal, LRU movement, reservation search, free-bit scanning, cannibalizing older reservations, and optional debug validation. The global `resv_lock` serializes all reservation maps.

## Control flow
Each reservation map is initialized with an OCFS2 superblock and later restarted with a disk bitmap and bitmap length. When allocation asks for reserved bits, `ocfs2_resmap_resv_bits` creates a window if the reservation is empty, sizing it from `osb_resv_level`, directory reservation level, or the requested temporary length. Search starts near the previous allocation, scans gaps between rb-tree windows for clear disk bits, retries from zero, and finally cannibalizes the oldest LRU reservation if no free gap is found. After allocation succeeds, `ocfs2_resmap_claimed_bits` shrinks or discards the consumed left side of the reservation and records the last allocation as the next search goal.

## State and persistence
Reservation state is entirely in memory: rb-tree windows, per-reservation start/length, last allocation, flags, and LRU list membership. It references the current disk bitmap but does not persist anything to disk. Restarting a map discards all windows because the bitmap window has changed.

## Dependencies and integration points
It depends on Linux rbtrees/lists/bitops and OCFS2 bitmap bit helpers. It integrates with local allocation and suballocation code that owns the actual on-disk bitmap and calls the reservation API before and after claiming bits.

## Risks and test signals
Risks include stale `m_disk_bitmap` after local-alloc window movement, overlap in rb-tree windows, cannibalizing a reservation still expected by a caller, off-by-one range handling at bitmap end, global spinlock contention, and disabled reservation levels returning `-ENOSPC` as a control signal. Test signals include sequential file growth locality, temporary reservations, directory reservation policy, map restart while reservations exist, full bitmap behavior, LRU cannibalization, debug reservation validation, and allocation at the last bit of the bitmap.
