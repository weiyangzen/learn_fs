# File Research: sources/block-storage/linux-dm/drivers/md/dm-stats.c

## Purpose
Implements per-mapped-device I/O statistics regions controlled by DM messages. It records reads/writes, sectors, merges, service time, in-flight I/O, queue time, optional precise timestamps, and optional latency histograms.

## Main Objects
- `struct dm_stat_percpu`: per-CPU counters for one region entry.
- `struct dm_stat_shared`: shared in-flight counters, timestamp, and temporary totals.
- `struct dm_stat`: one statistics region with ID, range, step, flags, histogram boundaries, program/aux strings, per-CPU arrays, and flexible shared entries.
- `struct dm_stats_last_position`: per-CPU last sector/RW used to infer merged I/O.

## Public Surface
- `dm_statistics_init()` / `dm_statistics_exit()`
- `dm_stats_init()` / `dm_stats_cleanup()`
- `dm_stats_message()`
- `dm_stats_account_io()`
- Module parameter `stats_current_allocated_bytes`.

## Control Flow
- `dm_stats_init()` initializes the stats list, mutex, and per-CPU last-position tracking.
- `dm_stats_message()` dispatches `@stats_*` commands:
  - `@stats_create`
  - `@stats_delete`
  - `@stats_clear`
  - `@stats_list`
  - `@stats_print`
  - `@stats_print_clear`
  - `@stats_set_aux`
- `message_stats_create()` parses a sector range, step or divisor, feature arguments, program ID, and auxiliary data, then calls `dm_stats_create()`.
- `dm_stats_create()` calculates entry counts, allocation sizes, checks memory caps, allocates shared/per-CPU/histogram storage, suspends the mapped device to start exactly, assigns the lowest available ID, and inserts the region using RCU list insertion.
- `dm_stats_account_io()` is called at I/O start/end, computes merge and precise-duration metadata, then walks all RCU-visible stat regions and updates overlapping entries.
- `dm_stats_print()` folds per-CPU counters into temporary shared totals, prints region-entry counters, optionally histogram buckets, and optionally clears by subtracting snapshots of totals.
- `dm_stats_delete()` removes a region with RCU protection and chooses synchronous or callback freeing depending on whether vmalloc-backed allocations are present.

## Data and Accounting Rules
- Memory usage is globally capped to avoid user-created regions exhausting RAM or vmalloc space.
- Region ranges are split into fixed `step` entries; one bio may update multiple entries.
- Precise mode uses nanoseconds from `ktime_get()`, while normal mode uses jiffies and converts on print.
- Histograms use sorted ascending boundaries; binary search assigns buckets.
- On 32-bit architectures local IRQs are disabled around counter updates to avoid torn 64-bit updates; on 64-bit preemption is disabled.

## Dependencies
- DM core mapped-device stats ownership.
- RCU lists/callbacks.
- Per-CPU allocation and CPU-local update primitives.
- Kernel memory/vmalloc accounting and NUMA-aware allocation.

## Notable Behaviors
- Stats creation suspends/resumes the mapped device after allocation to avoid in-flight ambiguity.
- Buffer overflow for `@stats_create` is pre-tested because leaking a created region ID would otherwise be possible.
- `@stats_list` can filter by `program_id`.
- `@stats_print_clear` clears by subtracting current folded totals rather than zeroing all CPU counters.

## Risk and Test Focus
- Allocation-size overflow checks are critical due to user-controlled region sizes and histogram counts.
- RCU/freeing paths must handle both kmalloc and vmalloc storage correctly.
- Clear/print races are intentionally approximate but should not corrupt counters.
- Histogram parsing rejects unsorted or malformed boundaries; malformed input coverage matters.
