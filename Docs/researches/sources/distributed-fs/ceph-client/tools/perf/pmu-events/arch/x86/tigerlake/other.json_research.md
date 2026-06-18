# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/other.json

## Purpose
`other.json` holds four Tiger Lake events that do not fit cleanly into the neighboring cache, memory, frontend, FP, or pipeline files. They cover core power turbo-license levels and a streaming write offcore-response event.

## Important APIs, Types, and Fields
The file uses the same event schema as other Tiger Lake event arrays: `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, and `CORE_POWER.LVL2_TURBO_LICENSE` use event code `0x28` with different unit masks. `OCR.STREAMING_WR.ANY_RESPONSE` uses `MSRIndex`/`MSRValue`, so it depends on offcore response filter programming.

## Control Flow and Data Flow
Perf parses these entries into the Tiger Lake event table. Runtime users can request turbo-license cycle events to understand power/frequency license residency, or the OCR streaming write event to count matching offcore responses. The OCR record follows the same MSR-filtered data path as offcore events in `cache.json`.

## State and Persistence Behavior
The file stores static definitions only. Runtime state is hardware counter state over the measurement interval. Turbo license events represent cycles in license levels, while the OCR event represents filtered response counts; they should not be aggregated without clear normalization.

## Dependencies and Integration Points
The file depends on Tiger Lake core PMU support and, for OCR, kernel/perf support for programming offcore response MSRs. It integrates with power-oriented metric groups and with offcore/cache analysis when streaming writes matter.

## Risks and Edge Cases
The file's catch-all name can hide important event ownership; maintainers may accidentally duplicate events in more specific files. OCR resource conflicts are possible when combined with other offcore-filtered events. Turbo-license counters can be workload-, SKU-, and firmware-dependent, so zero or skewed residency may be normal.

## Test Signals
Validate JSON syntax and generated event tables. `perf list` should expose the three `CORE_POWER.*TURBO_LICENSE` events and `OCR.STREAMING_WR.ANY_RESPONSE`. Runtime tests can compare turbo-license cycles under scalar, AVX, and idle workloads, and separately verify the OCR event schedules with other offcore events or reports constraints cleanly.
