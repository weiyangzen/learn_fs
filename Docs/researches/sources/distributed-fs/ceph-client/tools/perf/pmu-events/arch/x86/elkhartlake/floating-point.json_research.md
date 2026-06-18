<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/floating-point.json

## Purpose
Provides three Elkhart Lake floating-point PMU aliases: divider busy cycles, floating-point microcode assists, and retired floating-point divide uops.

## Important APIs, Types, And Functions
The entries use the standard raw-event schema: `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. `MACHINE_CLEARS.FP_ASSIST` also carries `PEBS: 1`, marking it as a precise-capable event in generated perf descriptions.

## Control Flow
The build-time generator reads this file from the Elkhart Lake directory, lowercases names for generated aliases, and emits event strings such as `event=0xcd,umask=0x2`. Runtime perf users can request `CYCLES_DIV_BUSY.FPDIV`, `MACHINE_CLEARS.FP_ASSIST`, or `UOPS_RETIRED.FPDIV`; perf then programs the core PMU counter with the encoded event selector.

## State And Persistence
There is no source-level mutable state. The generated aliases persist in perf's PMU table; runtime state is the programmed counter and optional PEBS sampling stream for the assist event.

## Dependencies And Integration Points
Depends on perf's generic PMU JSON parser and the Elkhart Lake `core` PMU mapping. It complements broader pipeline events because FP assists can manifest as machine clears and divide busy cycles can explain backend stalls.

## Risks And Edge Cases
The file is small, so each encoding has high impact. Mislabeling `PEBS` for `MACHINE_CLEARS.FP_ASSIST` would affect precise sampling guidance. Workloads without x87/SSE divide or FP assists naturally report zero, which is not a collection failure.

## Test Signals
Validate JSON syntax and generated aliases. Hardware smoke tests can run divide-heavy floating-point loops with `perf stat -e CYCLES_DIV_BUSY.FPDIV,UOPS_RETIRED.FPDIV`; precise-sampling tests should confirm perf accepts the FP assist event when requested with precise modifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/floating-point.json -->
