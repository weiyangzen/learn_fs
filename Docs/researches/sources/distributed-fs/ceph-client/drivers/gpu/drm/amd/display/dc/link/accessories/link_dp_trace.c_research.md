# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/accessories/link_dp_trace.c

Purpose: lightweight DisplayPort link-training and eDP power trace helpers stored on `struct dc_link`.

Important APIs and functions: `dp_trace_init()` and `dp_trace_reset()` clear trace state; `dp_trace_detect_lt_init()` and `dp_trace_commit_lt_init()` clear separate detection/commit link-training traces; count helpers update total/fail/link-loss counts; result and logged-flag helpers track reporting state; timestamp setters/getters store LT start/end and eDP power on/off times; `dp_trace_source_sequence()` optionally writes a debug source-sequence value to DPCD.

Control flow: link-training code calls init/reset at lifecycle boundaries, increments totals/failures around LT attempts, records result and timestamps, and uses logged flags to avoid duplicate logging. eDP power code records power transition timestamps. Debug sequence writing is gated by `link != NULL` and `link->dc->debug.enable_driver_sequence_debug`.

State and persistence: all state is stored in `link->dp_trace`, including initialized flag, detect and commit traces, counts, timestamps, and eDP power timestamps. It persists for the link object lifetime until reset.

Dependencies and integration points: depends on `link_dp_trace.h`, DPCD protocol helpers, `dm_get_timestamp()`, and link-training result types. It integrates with DP training diagnostics and optional source-sequence debug DPCD writes.

Risks: functions generally assume non-NULL `link` except `dp_trace_source_sequence()`. `dp_trace_reset()` clears `is_initialized`, unlike detect/commit init helpers; callers must understand lifecycle. Timestamp values are only meaningful if the DC context clock is valid.

Test signals: link-training logs showing correct totals/failures/results, no duplicate logging when flags are set, eDP power timing traces, and DPCD source-sequence writes only when debug is enabled.
