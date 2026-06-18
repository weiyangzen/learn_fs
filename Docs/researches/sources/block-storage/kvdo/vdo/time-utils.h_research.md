# File Research: sources/block-storage/kvdo/vdo/time-utils.h

This header provides time helpers around kernel `ktime` APIs. `current_time_ns(clockid_t)` returns monotonic or realtime nanoseconds and is inline so constant clock ids compile to a single call.

It also defines inline second/nanosecond conversions:
- `seconds_to_ktime()`
- `ktime_to_seconds()`

The non-inline `current_time_us()` returns wall-clock microseconds. Includes come from local compiler/type definitions plus kernel time headers.
