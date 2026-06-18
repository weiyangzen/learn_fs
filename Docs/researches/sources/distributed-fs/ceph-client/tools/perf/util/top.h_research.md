# sources/distributed-fs/ceph-client/tools/perf/util/top.h

## Purpose

`top.h` defines the shared state structure for `perf top`.

## Important APIs, Types, and Functions

`struct perf_top` embeds a `perf_tool`, evlists, record options, event switch state, interval and total counters, display/filter settings, session pointer, terminal size, symbol filters, LBR stitching toggle, and a two-buffer ordered-event queue with mutex and condition variable. It declares header formatting and counter reset functions. It also defines `CONSOLE_CLEAR`.

## Control Flow and State

The struct is mutable live UI state. Sample processing updates counters and histograms; display code reads and resets interval counters; queue state coordinates event ingestion and rendering.

## Dependencies and Integration Points

It depends on the perf tool dispatch table, evswitch, annotate, ordered-events, record options, mutex/cond wrappers, and terminal ioctls. It is consumed by the `perf top` builtin.

## Risks and Test Signals

Risks include concurrent queue access, counter reset races, and platform differences in terminal clear behavior. Tests should focus on header rendering and queue rotation under event load.
