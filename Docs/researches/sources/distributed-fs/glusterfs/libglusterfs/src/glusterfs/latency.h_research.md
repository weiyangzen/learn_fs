# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/latency.h

## Purpose
Defines a compact latency accumulator for measuring operation durations in nanoseconds.

## APIs, Types, and Functions
`gf_latency_t` stores minimum, maximum, total, and count. APIs are `gf_latency_new(size_t n)` for arrays, `gf_latency_reset()`, and `gf_latency_update(gf_latency_t *lat, struct timespec *begin, struct timespec *end)`.

## Control Flow, State, and Persistence
Callers allocate one or more counters, reset them, and update with begin/end timestamps after operations. State is in-memory diagnostic data and usually tied to process or translator lifetime.

## Dependencies and Integration
Depends on `time.h` and integer types. Integrated with `glusterfs_ctx_t.measure_latency`, statedump/statistics paths, and operation profiling.

## Risks and Test Signals
Risks include non-monotonic timestamps if callers use unsuitable clocks, total overflow in long-running processes, unsynchronized concurrent updates, and min initialization mistakes. Test signals include reset/update unit tests, monotonic-clock integration checks, concurrent update review, and latency statedump validation.
