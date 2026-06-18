# File Research: sources/block-storage/lvm2/libdm/libdm-timestamp.c

## Summary
Implements a small opaque timestamp abstraction for libdm. It can use monotonic `clock_gettime()` when realtime support is configured, or fall back to `gettimeofday()`.

## Main Responsibilities
- Allocates, captures, compares, copies, and frees `struct dm_timestamp`.
- Converts timestamps to nanosecond counters for comparison and delta calculations.
- Hides platform-specific timestamp representation behind one libdm API.

## Key APIs
- `dm_timestamp_alloc()`
- `dm_timestamp_get()`
- `dm_timestamp_compare()`
- `dm_timestamp_delta()`
- `dm_timestamp_copy()`
- `dm_timestamp_destroy()`

## Important Behavior
With `HAVE_REALTIME`, timestamps use `CLOCK_MONOTONIC`, avoiding wall-clock jumps. Without it, the fallback uses `gettimeofday()` and is subject to wall-clock/NTP adjustments.

`dm_timestamp_compare()` returns `-1`, `0`, or `1` by comparing nanosecond totals. `dm_timestamp_delta()` returns the absolute nanosecond difference without preserving ordering.

## State and Lifetime
Timestamps are heap-allocated with `dm_zalloc()` and freed with `dm_free()`. The concrete struct differs by configuration: `timespec` for realtime, `timeval` for fallback.

## Risks
The API does not validate null inputs in compare/delta/copy. Callers must only pass allocated timestamp objects. The fallback mode is not monotonic.
