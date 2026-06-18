# sources/distributed-fs/ceph-client/include/linux/win_minmax.h

## Purpose
`win_minmax.h` declares a small windowed min/max tracker used by algorithms that need a running minimum or maximum over a recent time window without retaining every sample.

## Important APIs, Types, and Functions
`struct minmax_sample` stores a timestamp `t` and value `v`. `struct minmax` stores three samples. `minmax_get()` returns the current best sample value. `minmax_reset()` initializes all three slots to one sample and returns that value. `minmax_running_max()` and `minmax_running_min()` update the tracker for a window length, timestamp, and measured value.

## Control Flow
Callers initialize or reset the tracker, then feed monotonically advancing time and measurements into the running max/min functions. The implementation keeps representative samples to approximate or maintain the windowed extremum and expires old samples according to `win`.

## State and Persistence
State is the three-sample `struct minmax` embedded in the caller's object. It persists until reset or object destruction and has no durable backing.

## Dependencies and Integration Points
The header depends only on Linux integer types. It integrates with congestion-control and rate-estimation style code that needs compact windowed extrema.

## Risks
Correctness depends on callers providing consistent time units and window sizes. Timestamp wraparound behavior is implementation-sensitive. Resetting at the wrong time loses history. The API stores `u32` values only, so callers must scale larger measurements.

## Test Signals
Signals include monotonic sequences, changing extrema inside and outside the window, timestamp wrap tests, reset behavior, and integration tests where the tracked max/min controls rate or threshold decisions.
