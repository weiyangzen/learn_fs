# sources/distributed-fs/ceph-client/tools/perf/util/tsc.h

## Purpose

`tsc.h` declares perf timestamp/TSC conversion support.

## Important APIs, Types, and Functions

`struct perf_tsc_conversion` stores `time_shift`, `time_mult`, `time_zero`, `time_cycles`, `time_mask`, and capability bits. The header declares conversion, mmap-page reading, `rdtsc()`, `arch_get_tsc_freq()`, and time-conv event formatting.

## Control Flow and State

The header has no state. Architecture code may provide `rdtsc()` and `arch_get_tsc_freq()` implementations.

## Dependencies and Integration Points

It includes `event.h` for perf event types and is used by TSC conversion records, tool PMU frequency reporting, and timestamp-sensitive code.

## Risks and Test Signals

Risks are ABI drift with `perf_event_mmap_page` and missing architecture hooks. Build tests should cover x86 and non-x86 configurations.
