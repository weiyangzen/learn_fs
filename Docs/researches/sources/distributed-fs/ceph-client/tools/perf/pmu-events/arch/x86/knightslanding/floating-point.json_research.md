# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/floating-point.json

## Purpose

`floating-point.json` defines Knights Landing perf aliases for floating-point and SIMD-related core events. It contains three records: FP assist machine clears and two retired SIMD micro-op classifications.

These aliases help users measure expensive floating-point assists and the mix of packed versus scalar SIMD work across SSE, AVX, AVX2, and AVX-512 instructions on KNL.

## Important APIs, Types, and Schema

The file follows the perf event JSON schema:

- `MACHINE_CLEARS.FP_ASSIST` uses `EventCode: "0xC3"` and `UMask: "0x4"` to count floating operations retired that required microcode assists.
- `UOPS_RETIRED.PACKED_SIMD` uses `EventCode: "0xC2"` and `UMask: "0x40"` to count packed SIMD uops, excluding loads and packed byte/word multiplies.
- `UOPS_RETIRED.SCALAR_SIMD` uses `EventCode: "0xC2"` and `UMask: "0x20"` to count scalar SIMD uops, excluding loads, division, and sqrt.

All three records constrain measurement to core programmable counters `0,1` and include `SampleAfterValue` defaults. The two SIMD rows include `PublicDescription` text clarifying that the events are micro-op-level counts rather than instruction-level counts.

## Control Flow and Data Flow

When a user requests one of these event names, perf maps the alias to its raw event code and umask, then schedules it on one of the two generic core counters. No extra MSR programming is required.

The analytical data flow is straightforward: raw retired uop and machine-clear counts feed performance ratios or investigations. Packed and scalar SIMD events can be combined with instruction-retired, cycles, or memory events from sibling files to estimate vectorization quality and FP-assist overhead.

## State and Persistence Behavior

The file is static event metadata. It has no persistent runtime state beyond the event constants stored in the repository. The descriptions persist important interpretation rules: SIMD vector width is not reflected in the count, masks do not reduce the count, and most but not all instructions map to a single uop.

## Dependencies and Integration Points

This file depends on the perf PMU event-table parser and KNL core PMU selection. It integrates with `counter.json` through the two generic core counters and with `pipeline.json` through shared event families (`MACHINE_CLEARS` and `UOPS_RETIRED`). Users commonly combine these events with fixed counters from `pipeline.json`, such as retired instructions and unhalted cycles.

## Risks and Edge Cases

The SIMD events are easy to overinterpret. They count micro-ops, not instructions, elements, or FLOPs. A 128-bit, 256-bit, and 512-bit packed operation each increments the counter the same way, and masked-off lanes still count. That makes these events unsuitable as direct FLOP counters without architecture-specific scaling and instruction mix knowledge.

`MACHINE_CLEARS.FP_ASSIST` measures pipeline disruption due to assists, not a taxonomy of which operation caused the assist. Workloads with denormals, exceptions, or unsupported fast paths may need additional context to explain the count.

## Test Signals

Checks should ensure the file parses as a three-element JSON array, all `EventName` values are unique, all records have `EventCode`, `UMask`, `Counter`, and descriptions, and `perf list` exposes the three aliases under the KNL event map. Runtime smoke tests can attempt `perf stat -e MACHINE_CLEARS.FP_ASSIST,UOPS_RETIRED.PACKED_SIMD,UOPS_RETIRED.SCALAR_SIMD` on KNL-compatible systems or generated-table tests.
