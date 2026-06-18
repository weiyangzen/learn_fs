# File Research: sources/block-storage/kvdo/vdo/logical-zone.c

Logical-zone creation, drain/resume orchestration, LBN operation map setup, allocation selector setup, and flush-generation tracking.

Key responsibilities:
- Allocates and initializes `struct logical_zones` and each `logical_zone`.
- Creates per-zone `int_map` for LBN operations and allocation selectors.
- Creates default logical-zone threads and an action manager for zone-wide admin operations.
- Frees logical zones, selectors, and LBN operation maps.
- Drains logical zones through admin-state machinery, completing when no writes or notifications remain.
- Resumes logical zones from quiescent state.
- Tracks per-zone flush generations and active write VIOs.
- Acquires/releases a write data VIO’s flush-generation lock.
- Notifies the flusher when the oldest active generation advances.
- Dumps logical-zone state for debugging.

Important behavior:
- Each logical zone is tied to a configured logical-zone thread and block-map zone.
- `write_vios` list order is used to determine the oldest active flush generation.
- `vdo_increment_logical_zone_flush_generation()` increments the generation, resets per-generation I/O count, and updates oldest active generation.
- `vdo_acquire_flush_generation_lock()` rejects acquisition unless zone admin state is normal.
- Releasing a generation lock removes the VIO from `write_vios`; if oldest active generation advances and no notification is already in flight, it launches a completion to the flusher thread.
- Notification completion returns to the logical-zone thread and may chain additional notifications until caught up.
- Drain completion waits for no active writes and no in-flight flusher notification.

Dependencies:
- Action manager, admin state, allocation selector, block map, completion, constants, data VIO, flusher, `int-map`, logger, memory allocation, assertions, and VDO thread configuration.

Notable risks:
- Correctness relies on operations running on the zone thread; assertions are log-only.
- `ios_in_flush_generation` is incremented but not decremented here; it is a generation counter/stat, not active count.
- Drain can be delayed by a pending flusher notification even after writes are gone.
