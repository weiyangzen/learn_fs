# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/fdm.h

Purpose: Faults-disabled-mapping hash table used by direct IO to avoid page-fault deadlocks.

Key APIs and behavior:
- Fixed-size 3-way cuckoo-style table keyed by current task.
- `fdm_set()` records current task's mapping and waits on a closure waitlist if all candidate slots are occupied.
- `fdm_get()` retrieves current task's mapping.
- `fdm_set_dropped_locks()` sets a low-bit flag in the mapping word.
- `fdm_dropped_locks()` tests that flag.
- `fdm_clear()` removes current task and wakes waiters.
- `fdm_init()` zeroes the table and seeds independent hash functions.

Integration:
- Used by direct IO write mapping/page-fault coordination in `direct.c`.
- Intended to replace a removed per-task `faults_disabled_mapping` field.
- Uses `closure_waitlist`, random seeds, and lockless READ/WRITE_ONCE with barriers.

Risks and invariants:
- Only the owning current task should insert/remove its entry.
- Low bit of `address_space *` is stolen for dropped-lock signaling, relying on pointer alignment.
- Recursive retry in `fdm_set()` handles lost races after wakeup.
