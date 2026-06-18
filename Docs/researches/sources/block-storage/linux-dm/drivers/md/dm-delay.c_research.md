# File Research: sources/block-storage/linux-dm/drivers/md/dm-delay.c

## Role
Implements the `delay` device-mapper target, which remaps bios to one or more lower devices while delaying read, write, and optionally flush classes by configurable millisecond intervals.

## Target Interface
- Constructor accepts exactly 3, 6, or 9 arguments.
- Three arguments define a single class used for reads, writes, and flushes: `<device> <offset> <delay>`.
- Six arguments define separate read and write classes, with flush using the write class.
- Nine arguments define independent read, write, and flush classes.

## Core Mechanics
- `struct delay_class` stores the lower device, start sector, delay in milliseconds, and count of delayed operations.
- `delay_map()` chooses a class based on bio direction and `REQ_PREFLUSH`, remaps the bio to the class device/start, then calls `delay_bio()`.
- Delayed bios store `struct dm_delay_info` in per-bio data, including class pointer and expiration jiffies.
- A global `delayed_bios_lock` protects each target's delayed list; a per-target timer schedules a work item when the next bio expires.
- `flush_expired_bios()` drains expired bios into a local list and submits them outside the list lock.
- `delay_presuspend()` disables new delays, cancels the timer, and flushes all queued bios.

## Status and Device Iteration
- Info status reports queued operation counts for read, write, and flush classes.
- Table status reconstructs only the classes explicitly supplied in the original argument count.
- `iterate_devices` reports all three class devices, even if they refer to the same underlying device.

## Important Invariants
- Bios already have their target device and sector rewritten before being delayed.
- `may_delay` prevents suspend from racing in new delayed bios after the flush-all path begins.
- Timer updates are serialized by `timer_lock` so the earliest expiry is preserved.

## Filesystem/Storage Relevance
This is a timing/fault-injection target for block-stack testing. It can model asymmetric read/write/flush latency and can expose ordering or timeout assumptions in filesystems and upper storage layers.

## Notable Risks
- The delayed bio list lock is global rather than per-target.
- Delays are based on jiffies and workqueue scheduling, so timing is approximate.
