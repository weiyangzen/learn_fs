# sources/distributed-fs/ceph-client/tools/perf/util/tp_pmu.h

## Purpose

`tp_pmu.h` declares tracepoint PMU discovery and enumeration helpers.

## Important APIs, Types, and Functions

It defines callback typedefs `tp_sys_callback` and `tp_event_callback`, declares tracepoint ID lookup, per-system and per-event iteration, PMU classification, PMU event enumeration, event counting, and existence checking.

## Control Flow and State

The API is callback-driven and has no header-level state.

## Dependencies and Integration Points

It includes `pmu.h` for `struct perf_pmu` and PMU event callback types. It is used by PMU enumeration and tracepoint event parsing paths.

## Risks and Test Signals

Callback users must tolerate negative errno returns and live tracefs changes. Compile tests should cover callback signatures.
