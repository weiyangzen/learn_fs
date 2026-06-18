
# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-gpci-requests.h

## Purpose

This macro-driven include file lists hypervisor GPCI counter request definitions used by request-generation headers to produce GPCI perf event metadata and structures.

## Important APIs, Types, And Functions

- The file includes `req-gen/_begin.h`, repeatedly defines `REQUEST_NAME`, `REQUEST_NUM`, and `REQUEST_IDX_KIND`, includes `I(REQUEST_BEGIN)`, emits a `REQUEST(...)` body of `__field`, `__array`, and `__count` entries, then includes `I(REQUEST_END)`.
- It defines request groups such as `dispatch_timebase_by_processor` (`0x10`), partition entitlement/consumption (`0x20`), `system_performance_capabilities` (`0x40`), several optional bus/core utilization requests under `ENABLE_EVENTS_COUNTERINFO_V6`, hypervisor queuing/times requests (`0xE0`, `0xF0`, `0xF4`), and `partition_instruction_count_and_time` (`0x100`).
- `__count` entries are intended to become perf-exposed counters; `__field` and `__array` entries describe normal metadata and padding.

## Control Flow

There is no direct runtime control flow. The file is processed by macro includes to generate code/data for each request. Conditional compilation includes older counter-info v6 request sets only when enabled.

## State And Persistence

No runtime state. The definitions are compile-time metadata derived from the `getPerfCountInfo v1.07` document.

## Dependencies And Integration Points

It depends on the `req-gen` macro framework, `hv-gpci` request numbering, and the hypervisor GPCI hcall ABI. `hv-common.c` uses the generated `HV_GPCI_system_performance_capabilities` request identifier and response shape.

## Risks And Edge Cases

The generator requires byte sizes for `__count` and `__field` to be decimal numeral tokens, not expressions or hex. A comment notes a suspected spec error for `system_tlbie_count_and_time` offset. Several request types are intentionally skipped because they have no counters. Conditional v6 events may not apply to newer counter-info versions.

## Test Signals

Build the GPCI driver with and without `ENABLE_EVENTS_COUNTERINFO_V6`, inspect generated sysfs events, verify hcall request numbers and starting-index kinds, and compare counter offsets against hypervisor documentation and real `perf stat` results.
