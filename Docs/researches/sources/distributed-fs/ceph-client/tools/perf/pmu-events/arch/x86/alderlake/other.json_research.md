# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/other.json

## Purpose

This small 11-entry catalog holds Alder Lake PMU events that do not fit cleanly into the cache, frontend, memory, floating-point, pipeline, or uncore buckets. It covers hardware and page-fault assists, core power license levels, last-branch-record insertion, streaming-write offcore responses, and XQ full cycles. Seven records target `cpu_core` and four target `cpu_atom`.

## Important APIs, Types, and Data

The entries use the standard perf event schema and selected optional fields: `Deprecated`, `CounterMask`, `MSRIndex`, and `MSRValue`. Event families are `ASSISTS`, `CORE_POWER`, `LBR_INSERTS`, `OCR`, and `XQ`. The `OCR.*STREAMING_WR*` entries use offcore response MSRs `0x1a6,0x1a7`; there are both atom-specific full/partial streaming-write records and a shared `OCR.STREAMING_WR.ANY_RESPONSE` name with core and atom encodings. `LBR_INSERTS.ANY` is deprecated for atom.

## Control Flow

There is no local execution. Perf consumes the JSON into alias tables and later programs PMU events when users request these miscellaneous aliases or when metrics depend on them. For `OCR` records, the runtime path includes model-specific register programming. For power license events, perf counts package/core throttling-license cycles or occurrences through normal programmable counters.

## State and Persistence Behavior

The JSON persists event aliases and encodings. Counts live only in active perf sessions and hardware counters. Deprecated status is persistent compatibility metadata. The offcore response masks are persistent source data and represent the semantic boundary between full, partial, and generic streaming-write events.

## Dependencies and Integration Points

This file integrates with perf's Alder Lake event table generation, hybrid PMU routing, `perf list`, power/performance throttling analysis, assist diagnostics, LBR-related profiling, and offcore streaming-write metrics. It depends on kernel PMU support for the listed core and atom encodings and on offcore response MSR support for `OCR` events.

## Risks

The catch-all nature of the file makes discoverability and metric dependencies easy to miss. Deprecated `LBR_INSERTS.ANY` should not be preferred by new metrics. Streaming-write events rely on MSR filters and can silently change meaning if masks are wrong. `CORE_POWER.LICENSE_*` events can be platform-sensitive and may need careful interpretation under frequency scaling, turbo, thermal throttling, and power-limit policies.

## Test Signals

Validation should cover schema parsing, `perf list` visibility, deprecation display, offcore MSR encoding checks for streaming-write aliases, and smoke measurements on workloads that trigger assists, page faults, power-license transitions, and non-temporal or streaming stores. Metrics using this file should be tested for both core and atom PMU availability.
