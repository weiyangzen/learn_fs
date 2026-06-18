# sources/distributed-fs/glusterfs/libglusterfs/src/latency.c

## Purpose
`latency.c` provides small helpers for per-FOP latency accounting. Translators and call frames use it to allocate/reset latency arrays and to update min, max, total, and count statistics from operation begin/end timestamps.

## Important APIs, Types, And Functions
`gf_latency_new(size_t n)` allocates an array of `gf_latency_t` records and resets each entry. `gf_latency_reset(gf_latency_t *lat)` clears a record and initializes `min` to `ULLONG_MAX` so the first measured value wins. `gf_latency_update(gf_latency_t *lat, struct timespec *begin, struct timespec *end)` computes elapsed time with `gf_tsdiff()` and updates max/min/total/count. `gf_frame_latency_update(call_frame_t *frame)` maps a frame operation to `frame->this->stats[op].latencies`.

## Control Flow
Allocation is straightforward: allocate `n * sizeof(*lat)` through `GF_MALLOC`, then reset each slot. Updates first reject measurements where either timestamp has zero `tv_sec`, which covers runtime toggling of latency measurement. Frame updates backfill `frame->op` from `frame->root->op` when unset, validate it against `GF_FOP_MAXVALUE`, log invalid values, then update the translator stats slot.

## State And Persistence
Latency records are in-memory counters. This module does not own persistence and does not lock; it assumes callers provide valid storage and appropriate synchronization. Counters are later consumed by monitoring/statedump-style code such as `monitoring.c`.

## Dependencies And Integration Points
Dependencies are `glusterfs/logging.h` and `glusterfs/statedump.h` for types and utility functions. The integration points are `call_frame_t`, translator `stats[]`, `gf_fop_list`-indexed operation IDs, and `gf_tsdiff()` from the time utilities.

## Risks
The update functions do not validate NULL `lat`, `begin`, or `end`. Concurrent updates to the same `gf_latency_t` are non-atomic and can lose increments or tear min/max/total on weak architectures. `min` reset to `ULLONG_MAX` is meaningful only if dumping code treats zero count specially. Skipping timestamps with zero seconds means operations around epoch-zero are ignored, which is acceptable for runtime Gluster processes.

## Test Signals
Unit tests should exercise reset initialization, first-update min behavior, max/min updates over increasing and decreasing samples, zero timestamp skip, frame op fallback, invalid op logging path, and aggregate average compatibility with `monitoring.c`.
