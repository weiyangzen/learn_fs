# sources/distributed-fs/ceph-client/kernel/trace/trace_benchmark.h

## Purpose
`trace_benchmark.h` declares the `benchmark` tracepoint system and defines the `benchmark_event` trace event used by `trace_benchmark.c` to measure tracepoint write overhead.

## Important APIs, types, and functions
It declares `trace_benchmark_reg()` and `trace_benchmark_unreg()`, defines `BENCHMARK_EVENT_STRLEN` as 128, and uses `TRACE_EVENT_FN(benchmark_event, ...)` with two fields: a fixed string payload `str[128]` and a `u64 delta`. The event print format is `"%s delta=%llu"`.

## Control flow
The `TRACE_EVENT_FN` macro generates the normal tracepoint enable, emit, and format code while binding enable/disable callbacks to the registration functions. `TP_fast_assign` copies the provided string into the event record and stores the measured delta. The include path/footer selects this local file as the trace include and includes `<trace/define_trace.h>` outside the guard, which is required for tracepoint definition generation.

## State and persistence behavior
The header itself holds no mutable state. It defines the ABI and generated code contract for the event record stored in ring buffers and exposed through tracefs event format files.

## Dependencies and integration points
It depends on `<linux/tracepoint.h>` and the trace event macro framework. The registration callbacks integrate with `trace_benchmark.c`, and the generated event appears under the `benchmark` tracepoint system.

## Risks
Changing field names, sizes, or print format would change user-visible tracefs ABI. The fixed string copy uses the full 128-byte payload, so producers must provide a buffer of at least that size, as `trace_benchmark.c` does with `bm_str`.

## Test signals
Build-time trace event generation is the main signal. At runtime, `/sys/kernel/tracing/events/benchmark/benchmark_event/format` should expose the `str` and `delta` fields, and enabling the event should call the registration hook.
