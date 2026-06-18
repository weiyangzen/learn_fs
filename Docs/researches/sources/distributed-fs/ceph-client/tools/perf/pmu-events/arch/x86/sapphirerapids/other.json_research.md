# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/other.json

## Purpose
`other.json` defines six Sapphire Rapids core PMU events that do not fit cleanly into the cache, frontend, memory, floating-point, or pipeline category files. The coverage is page-fault assists, hardware interrupts, a streaming-write OCR catch-all, and cycles where the allocation queue is full.

## Important APIs, types, and schema fields
Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. `XQ.FULL_CYCLES` uses `CounterMask=1` to count cycles. `OCR.STREAMING_WR.ANY_RESPONSE` uses the offcore response pattern with `EventCode` `0x2A,0x2B`, `UMask` `0x1`, `MSRIndex` `0x1a6,0x1a7`, and `MSRValue` `0x10800`.

## Control flow and integration
Build-time generation includes these events in the same Sapphire Rapids PMU table as the larger category files. Runtime users see names such as `ASSISTS.PAGE_FAULT`, `HW_INTERRUPTS.RECEIVED`, and `XQ.FULL_CYCLES` through `perf list`; event parsing then programs core counters or OCR MSRs as appropriate. The file acts as an overflow category while still following the same schema contract.

## State and persistence behavior
The file persists a small set of hardware encodings and descriptions. Runtime interrupt, assist, queue, and streaming-write counts are held in PMU counters and offcore MSR state. There is no local state or generated artifact in this source file beyond perf's normal build output.

## Dependencies
Dependencies include Sapphire Rapids core PMU event selectors for assists and interrupts, the offcore response MSRs for streaming writes, and perf's event generator. It integrates with broader metric groups such as `OS`, `Pipeline`, `MemOffcore`, and `tma_assists_group` when metrics reference these event names.

## Risks and edge cases
Small category files are easy to overlook during schema migrations. `OCR.STREAMING_WR.ANY_RESPONSE` must stay consistent with streaming-write events in `cache.json` and `memory.json`. Interrupt and page-fault assist counts are workload and OS sensitive, so tests should avoid asserting exact values outside controlled microbenchmarks. `XQ.FULL_CYCLES` depends on `CounterMask` semantics; dropping that field changes count meaning from cycles to raw occurrences.

## Test signals
Use `jq empty`, generated PMU table builds, and `perf list` filtering for `ASSISTS`, `HW_INTERRUPTS`, `OCR.STREAMING_WR`, and `XQ`. Runtime smoke tests can use interrupt-heavy workloads, page-fault inducing memory access, and streaming-store loops to check that counts are nonzero in expected scenarios. Static checks should verify the streaming-write OCR row retains `MSRIndex` and `MSRValue`.
