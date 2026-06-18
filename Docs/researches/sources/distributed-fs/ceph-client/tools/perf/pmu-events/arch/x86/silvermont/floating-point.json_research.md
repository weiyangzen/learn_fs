# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/floating-point.json

## Purpose
Defines the Silvermont floating-point assist event exposed to perf. The one-entry JSON array maps `MACHINE_CLEARS.FP_ASSIST` to the PMU encoding used to count stalls due to floating-point assists.

## Important APIs, Types, And Event Groups
The object uses perf's core event schema: `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and `Counter`. The event is encoded as event code `0xC3` with umask `0x4`, sharing the broader machine-clear event family with memory-ordering, self-modifying-code, and all-clears entries in sibling files.

## Control Flow
Perf parses the single alias at build time and resolves it at runtime to a core PMU event. There is no in-file execution. In analysis, users select the alias to attribute stall or clear activity to FP assists rather than to other machine-clear causes.

## State And Persistence
The file persists only the alias metadata. Runtime counts are maintained by hardware and perf event state during measurement. Sampling behavior is controlled by `SampleAfterValue` and perf command options, not by any mutable state in this file.

## Dependencies And Integration Points
It depends on Silvermont core PMU support and perf's event-table infrastructure. It integrates with `pipeline.json` because that file defines other `MACHINE_CLEARS.*` aliases using the same event code, and with floating-point performance investigations where FP assist counts are correlated with instruction mixes and exception/denormal behavior.

## Risks
The main risk is semantic isolation: counting FP assists as machine clears may be confused with all machine clears if users also select aggregate events. Because this is a single specialized event, an incorrect umask would remove most of the file's value while remaining syntactically valid.

## Test Signals
Use JSON validation and perf list generation. Runtime validation requires a Silvermont target and a workload likely to trigger FP assists, such as denormal or exceptional floating-point operations, then checking that this alias moves independently from aggregate machine-clear counters.
