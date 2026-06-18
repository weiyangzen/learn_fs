# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/other.json

## Purpose

`other.json` defines miscellaneous Emerald Rapids core PMU events that do not fit the more specific perf event category files. It contributes six event records to the Linux perf PMU event database: page-fault assists, hardware interrupt states, streaming-store offcore response counting, and uncore request queue full cycles.

This is declarative hardware counter metadata. It gives perf enough information to program counters and MSR filters for named events; it does not collect samples or implement counter logic itself.

## Important APIs, Types, and Data

The file is a JSON array of event objects following the perf PMU event schema. Common fields include `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. `XQ.FULL_CYCLES` also uses `CounterMask`; `OCR.STREAMING_WR.ANY_RESPONSE` uses `MSRIndex` and `MSRValue` to configure offcore response filtering.

The event families are:

- `ASSISTS.PAGE_FAULT`, event code `0xc1`, umask `0x8`, counting page-fault assists on programmable counters 0 through 7.
- `HW_INTERRUPTS.MASKED`, `HW_INTERRUPTS.PENDING_AND_MASKED`, and `HW_INTERRUPTS.RECEIVED`, event code `0xcb`, distinguishing masked, pending-and-masked, and received hardware interrupts.
- `OCR.STREAMING_WR.ANY_RESPONSE`, event codes `0x2A,0x2B`, MSRs `0x1a6,0x1a7`, and MSR value `0x10800`, counting streaming stores with any response on counters 0 through 3.
- `XQ.FULL_CYCLES`, event code `0x2d`, umask `0x1`, counter mask `1`, counting cycles where the uncore cannot accept further core requests.

## Control Flow

There is no internal control flow. Perf's event loader reads the array, indexes entries by `EventName`, and uses the encoding fields when users request an event by name. For plain programmable events, perf programs the selected counter with `EventCode`, `UMask`, and any qualifier fields such as `CounterMask`. For the OCR event, perf must also program the listed model-specific register filter values before counting the offcore response event.

## State and Persistence Behavior

The JSON file is persistent source metadata. Runtime state consists of hardware counter values, overflow periods derived from `SampleAfterValue`, and MSR programming performed by perf or the kernel PMU driver. None of that state is stored in this file. The `Counter` field constrains where perf may schedule each event, and the MSR fields create a temporary hardware configuration while the event is active.

## Dependencies and Integration Points

The file depends on Linux perf's PMU event JSON parser, the x86 Emerald Rapids model mapping, and kernel PMU support for the encoded core events and offcore response MSRs. It integrates with `perf list`, `perf stat`, `perf record`, event alias resolution, counter scheduling, PEBS or sampling period setup where applicable, and tests that compare event encodings against upstream Linux or Intel PMU data.

The interrupt and assist counters are useful integration points for OS and low-level runtime diagnosis. The OCR streaming store event bridges core PMU event selection with MSR-filtered offcore response counting. `XQ.FULL_CYCLES` ties core pipeline observation to pressure at the core-to-uncore request interface.

## Risks and Edge Cases

MSR-backed events are higher risk than simple events. If `MSRIndex`, `MSRValue`, or allowed counters are wrong, perf may program an invalid offcore response filter, count a different transaction class, or fail to schedule the event. The two event codes for `OCR.STREAMING_WR.ANY_RESPONSE` imply paired offcore response facilities; tooling must support the comma-separated encoding form.

Counter constraints matter. The OCR and XQ events are limited to counters 0 through 3, while assists and interrupts can use counters 0 through 7. Ignoring those constraints can cause schedule failures or inaccurate multiplexing assumptions.

Several events have terse `BriefDescription` values without a richer `PublicDescription`. Users and tests may need external PMU documentation to distinguish exact semantics. Interrupt counts are sensitive to privilege, masking behavior, virtualization, and kernel configuration, so observed values may be workload and environment dependent.

## Test Signals

Validation should include JSON parsing, perf PMU table generation, `perf list` visibility for all six event aliases, and event encoding checks for `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, and `MSRValue`. Practical smoke tests include `perf stat -e ASSISTS.PAGE_FAULT`, `perf stat -e HW_INTERRUPTS.RECEIVED`, and scheduling checks for `OCR.STREAMING_WR.ANY_RESPONSE` on Emerald Rapids hardware or a perf event parser test fixture. Drift checks against upstream Linux perf PMU data are important for this vendored copy.
