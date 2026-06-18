# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/timespec.h

Purpose: `timespec.h` provides time helpers for monotonic/realtime timestamps, arithmetic, and comparison.

Important APIs and types: macros `TS`, `NANO`, and `GIGA` convert or scale nanosecond values. APIs include `timespec_now`, `timespec_now_realtime`, `timespec_now_monotonic_raw`, `timespec_adjust_delta`, `timespec_sub`, and `timespec_cmp`.

Control flow and state: functions fill or manipulate caller-provided `struct timespec` values. No global state is declared.

Dependencies and integration: `stack.h` uses `timespec_now` for frame latency. `timer.h` uses timespec deadlines. Syncop and latency/stat systems rely on accurate comparisons and deltas.

Risks: `TS(ts)` can overflow if applied to very large seconds values. Realtime versus monotonic selection matters for timers and latency; wall-clock changes should not skew monotonic measurements. Nanosecond normalization is required after add/subtract.

Test signals: compare/subtract edge cases, nanosecond borrow/carry, monotonic non-decreasing behavior, realtime availability, and latency measurement sanity tests should be included.
