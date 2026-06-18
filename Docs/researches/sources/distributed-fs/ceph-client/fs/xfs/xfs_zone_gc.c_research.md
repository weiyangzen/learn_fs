# sources/distributed-fs/ceph-client/fs/xfs/xfs_zone_gc.c

## Purpose
`xfs_zone_gc.c` implements background garbage collection for zoned XFS. It evacuates live realtime extents from partially used zones into reserved GC zones, remaps file data after successful IO, and resets zones that become empty.

## Important APIs, types, and functions
Public entry points are `xfs_zoned_need_gc`, `xfs_zone_gc_reset_sync`, `xfs_zone_gc_start`, `xfs_zone_gc_stop`, `xfs_zone_gc_wakeup`, `xfs_zone_gc_mount`, and `xfs_zone_gc_unmount`. Internal state includes `struct xfs_zone_gc_data`, `struct xfs_gc_bio`, and `struct xfs_zone_gc_iter`. Key helpers query and sort rmap records, pick victims from used buckets, select or steal GC target zones, allocate reserved GC blocks, pipeline read/write/reset bios, and finish remaps through `xfs_zoned_end_io`.

## Control flow
The GC kthread sleeps until space thresholds or reset work require action. It drains completed reset bios, completed writes, completed reads, and then starts new chunks. Victim selection walks reclaimable buckets from least used upward and avoids zones already under GC. Rmap records are gathered in batches, sorted by owner and offset, read into a scratch ring, written to a GC target zone with zone append splitting when needed, then remapped after direct IO/layout exclusion confirms no competing file writer invalidated the old mapping. Empty zones are flushed, log-forced, reset or discarded, marked free, and credited back to availability.

## State and persistence
Runtime state includes the scratch folio ring, bioset, reading/writing/resetting lists, victim iterator, GC target open zone, `rtg_gccount`, and `zi_reset_list`. Persistent effects include new file bmap entries, freed old extents, rmap used-counter updates, log-forced rmap state before reset, and hardware zone reset/discard state.

## Dependencies and integration points
It integrates with rtrmapbt, inode cache, bmap/remap code in `xfs_zone_alloc.c`, block zone reset/append/discard, memalloc NOFS, freezer/parkable kthreads, errortags, XFS stats, and zoned free-counter reservations.

## Risks and test signals
Risks include data movement races with user writes, reflink incompatibility, scratch ring wrap, zone append split alignment, stealing open zones after unclean shutdown, reserved-pool exhaustion, failure to decrement `rtg_gccount`, reset ordering before log persistence, and remount/shutdown wakeups. Test signals include low-space GC thresholds, tiny GC target capacity, injected read/write/reset failures, deleted inode rmaps, direct IO racing GC, mount after interrupted GC, and non-sequential conventional reset fallbacks.
