# sources/distributed-fs/ceph-client/lib/win_minmax.c

## Purpose
Implements Kathleen Nichols' constant-space windowed min/max tracker. It approximates the best value over a moving time interval by retaining best, second-best, and third-best samples instead of storing the whole window.

## APIs and control flow
Exports `minmax_running_max` and `minmax_running_min`, both operating on caller-owned `struct minmax` and `struct minmax_sample` values from `linux/win_minmax.h`. Each update resets the tracker when a new best value arrives or the third candidate has aged beyond the window. Otherwise, the new measurement may replace the second or third candidate. `minmax_subwin_update` promotes candidates when the best expires and seeds second/third choices after one-quarter and one-half of the window.

## State, dependencies, and integration
All persistent state lives in the caller's `struct minmax`; the file has no globals. Timestamp math uses wrapping `u32` subtraction, so callers must provide monotonic timestamps in units matching `win`. The helper integrates with networking and metric paths that need cheap moving-window RTT or latency extrema.

## Risks and test signals
The algorithm is approximate, especially on monotonic streams. Wrong timestamp units, non-monotonic time, tiny windows, or unsynchronized shared state can produce misleading results. Tests should compare against exact sliding-window calculations for monotonic, flat, bursty, expiring, and timestamp-wrap cases.
