# sources/distributed-fs/ceph-client/tools/perf/util/tsc.c

## Purpose

`tsc.c` converts between perf nanosecond timestamps and hardware time-stamp-counter cycles, reads conversion parameters from the perf mmap page, and synthesizes `PERF_RECORD_TIME_CONV` events.

## Important APIs, Types, and Functions

Public functions are `perf_time_to_tsc()`, `tsc_to_perf_time()`, `perf_read_tsc_conversion()`, `perf_event__synth_time_conv()`, weak `rdtsc()`, and `perf_event__fprintf_time_conv()`.

## Control Flow and State

Conversion uses `time_zero`, `time_mult`, and `time_shift`; short-time support masks cycles relative to `time_cycles`. `perf_read_tsc_conversion()` loops on the mmap page seqlock, uses read barriers, retries up to 10000 times, and requires `cap_user_time_zero`. Synthesis fills a perf event and invokes a supplied process callback unless conversion is unsupported. Formatting prints base fields and extended short-time fields only when the record contains them.

## Dependencies and Integration Points

It depends on perf event mmap page ABI, event synthesis, machine/tool callbacks, barrier primitives, and debug output. It integrates with record headers and readers that need timestamp conversion.

## State and Persistence Behavior

There is no global state. Conversion data can be persisted into perf.data as `PERF_RECORD_TIME_CONV`.

## Risks and Test Signals

Risks include seqlock races, unsupported `cap_user_time_zero`, overflow in conversion arithmetic, and backward compatibility with shorter records. Tests should read a live mmap page, synthesize and process time-conv events, round-trip ns/cycles for known conversion values, and format old/new record sizes.
