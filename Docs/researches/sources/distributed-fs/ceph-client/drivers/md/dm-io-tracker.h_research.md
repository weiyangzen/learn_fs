# sources/distributed-fs/ceph-client/drivers/md/dm-io-tracker.h

### Purpose
`dm-io-tracker.h` provides a small inline helper for tracking in-flight sector counts and idle time for a Device Mapper component. It answers whether a device has been idle for a duration and records when I/O begins and ends.

### Important APIs, Types, And Functions
The only type is `struct dm_io_tracker`, containing a spinlock, `sector_t in_flight`, `idle_time`, and `last_update_time`. Inline APIs are `dm_iot_init`, `dm_iot_idle_for`, `dm_iot_idle_time`, `dm_iot_io_begin`, and `dm_iot_io_end`.

### Control Flow
Initialization sets up the spinlock, clears `in_flight` and `idle_time`, and records `last_update_time = jiffies`. `dm_iot_io_begin` adds a sector length under lock. `dm_iot_io_end` subtracts a nonzero sector length and, if the counter reaches zero, records the current `jiffies` as the idle start. Query functions take the same lock and return either elapsed idle jiffies or whether `jiffies` is after `idle_time + j`.

### State And Persistence Behavior
All state is volatile and in-memory. `in_flight` is sector-based, not bio-count-based, so callers must pass matching lengths to begin/end. `last_update_time` is initialized but not otherwise updated by these helpers in this version.

### Dependencies And Integration Points
The header depends on `linux/jiffies.h`, spinlocks, `sector_t`, and jiffies time comparison helpers. It is designed for inclusion by DM targets or core components that need low-overhead idle detection.

### Risks And Edge Cases
The helpers do not guard against underflow if callers end more sectors than they began. A zero-length end is ignored. Because `idle_time` is only meaningful when `in_flight` is zero, users must not inspect it without the helper or equivalent locking. IRQ-safe locking is used for query/end, while begin uses `spin_lock_irq`, so call sites should not already hold the same lock.

### Test Signals
Useful tests are balanced begin/end accounting, idle transition timing after the last end, no idle report while sectors remain in flight, zero-length end behavior, and jiffies wrap-safe comparisons through `time_after`.
