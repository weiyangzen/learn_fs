# File Research: sources/block-storage/linux-dm/drivers/md/dm-io-tracker.h

## Purpose
Defines a small inline helper for tracking in-flight I/O sectors and how long a device has been idle.

## Main Interfaces
- `dm_iot_init()` initializes the lock, zero in-flight count, and time fields.
- `dm_iot_idle_for()` reports whether there has been no in-flight I/O for at least a requested jiffies interval.
- `dm_iot_idle_time()` returns the current idle duration when idle.
- `dm_iot_io_begin()` adds sectors to the in-flight count.
- `dm_iot_io_end()` subtracts sectors and records `idle_time` when the count reaches zero.

## Control Flow
Callers increment the tracked sector count when I/O begins and decrement it when I/O completes. Idle queries take the spinlock, check for zero in-flight sectors, and compare current `jiffies` against the recorded idle timestamp.

## State And Synchronization
`struct dm_io_tracker` stores a spinlock, `in_flight` sector count, `idle_time`, and `last_update_time`. All public operations take the spinlock with IRQ-safe variants where needed. `last_update_time` is initialized but not otherwise used in this header.

## Integration Points
This is a header-only utility intended for DM targets or helpers that need cheap idle detection without owning a larger accounting subsystem.

## Notable Behaviors
- `dm_iot_io_end()` ignores zero-length completions.
- Idle time is only meaningful after the in-flight count reaches zero.
- There is no underflow protection beyond caller correctness.

## Risks And Review Focus
- Callers must pair begin/end sector counts exactly.
- Any future use of `last_update_time` must preserve the current lock discipline.
