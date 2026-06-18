# sources/distributed-fs/ceph-client/tools/perf/util/top.c

## Purpose

`top.c` contains shared helpers for `perf top`, primarily construction of the dynamic header line and periodic counter reset.

## Important APIs, Types, and Functions

`perf_top__header_snprintf()` formats sample rate, kernel/user/guest percentages, exact sample percentage, lost/drop counts, selected event, target identity, and CPU coverage. `perf_top__reset_sample_counters()` clears interval counters after a header is emitted.

## Control Flow and State

The formatter derives rates by dividing interval counters by `delay_secs`. It has separate non-guest and guest display paths. If only one event is active, it prints the sample period or frequency. It chooses target text from PID, TID, UID, or all-target mode and includes CPU list or count. It resets interval counters before returning.

## Dependencies and Integration Points

It depends on evlist/evsel, parse-events, symbol globals such as `perf_guest`, target settings in record options, and CPU maps. It is used by stdio and TUI refresh loops.

## Risks and Test Signals

Risks include divide-by-zero when no samples exist, header truncation, lost/drop counters resetting at the wrong time, and incorrect guest percentage math. Tests should format headers for PID/TID/UID/all targets, single and multi-event evlists, explicit CPU lists, guest mode, zero samples, and lost/drop counts.
