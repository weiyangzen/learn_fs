# File Research: sources/block-storage/linux-dm/drivers/md/md-bitmap.h

## Purpose
Defines MD bitmap on-disk format, in-memory counter encoding, bitmap state flags, bitmap storage structures, and the bitmap API used by MD personalities, recovery code, and clustered MD.

## Main Interfaces
- Bitmap versions: `BITMAP_MAJOR_LO`, `BITMAP_MAJOR_HI`, `BITMAP_MAJOR_CLUSTERED`, `BITMAP_MAJOR_HOSTENDIAN`.
- Counter encoding: `bitmap_counter_t`, `NEEDED_MASK`, `RESYNC_MASK`, `COUNTER_MAX`, `NEEDED()`, `RESYNC()`, `COUNTER()`.
- Layout constants: `PAGE_BITS`, `PAGE_BIT_SHIFT`, `PAGE_COUNTER_RATIO`, `PAGE_COUNTER_SHIFT`, `PAGE_COUNTER_MASK`, `BITMAP_BLOCK_SHIFT`.
- On-disk superblock: `bitmap_super_t`.
- In-memory state: `struct bitmap_page`, `struct bitmap`, nested `bitmap_counts`, and `bitmap_storage`.
- Public bitmap functions for lifecycle, write tracking, sync tracking, resize, cluster slot copying, daemon work, and write-behind waiting.

## Control Flow
This header documents the counter state machine: a clean chunk has counter zero and a clear on-disk bit; dirtying sets the persistent bit and raises the counter; daemon sweeps can reduce counters and eventually clear persistent bits; resync-needed and resync-active high bits coordinate recovery.

## State And Synchronization
`struct bitmap` contains the `counts.lock` spinlock, pending write counters, wait queues, storage page map, flags, dirty-clean state, sysfs dirent references, and cluster slot number. The state bits include stale bitmap, bitmap write error, and host-endian legacy format.

## Integration Points
Included by MD bitmap implementation and clustered MD. Exposes API used by MD make-request paths, recovery paths, sysfs status, and cluster bitmap transfer.

## Notable Behaviors
- `bitmap_super_t` is fixed at 256 bytes and includes UUID, events, events-cleared, sync size, state, chunk size, daemon sleep, write-behind, reserved sectors, cluster node count, and cluster name.
- Version 3 is host-endian and non-portable; version 4 is little-endian; version 5 is clustered.
- The header explicitly documents pointer hijacking as an emergency low-memory counter fallback.

## Risks And Review Focus
- Any change to `bitmap_super_t` must preserve on-disk compatibility and the 256-byte size assumption.
- Counter-bit definitions limit usable write counters to 14 bits; overflow handling depends on `COUNTER_MAX`.
- Users of the API must respect locking and lifecycle assumptions because the structure fields are exposed internally.
