# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/fdm.h

## Summary
Defines the faults-disabled-mapping table used by bcachefs direct I/O to replace removed per-task kernel fault tracking.

## Main Contents
- `struct fdm_slot` with task pointer and mapping pointer plus a low-bit dropped-locks flag.
- `struct fdm_hash` with three random hash seeds, a closure waitlist, and 512 slots.
- Helpers `fdm_get()`, `fdm_dropped_locks()`, `fdm_set_dropped_locks()`, `fdm_set()`, `fdm_clear()`, and `fdm_init()`.

## Important Behavior
Each task can install one current mapping. Lookup checks exactly three task-hashed slots. Insertion waits on a closure waitlist if all candidate slots are occupied, writes mapping first, uses a write barrier, then publishes task as the valid marker. Clearing removes the task marker, barriers, and wakes waiters.

The low bit of the mapping word records that a fault handler dropped and retook locks; direct I/O can then invalidate pagecache again and retry safely.

## Risks
The table is intentionally lockless and assumes each task writes only its own entry. Correctness relies on address-space pointer alignment for low-bit stealing, memory barriers around the task valid marker, and low occupancy of the fixed-size hash. `fdm_set()` retries recursively after a lost race.
