# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/counter.json

## Purpose
Declares the Silvermont PMU counter inventory for perf. The one-object JSON array states that the `core` PMU has four fixed counters and two generic programmable counters.

## Important APIs, Types, And Event Groups
The schema is the perf counter-description JSON object: `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. `Unit: "core"` binds the declaration to the core PMU. `CountersNumFixed: "4"` and `CountersNumGeneric: "2"` inform perf tooling and generated metadata about the hardware counter capacity available for Silvermont events.

## Control Flow
The file contains no branches or executable logic. Perf tooling parses it as metadata alongside the event catalogs. Runtime scheduling decisions happen in perf and the kernel, where the number of fixed and generic counters constrains how many events can be programmed without multiplexing.

## State And Persistence
The persistent state is static hardware-capacity metadata. It does not change at runtime and does not store counter values. Live event scheduling state belongs to perf event descriptors and kernel PMU context management.

## Dependencies And Integration Points
This file integrates with all Silvermont event catalog files in the same directory. It is especially relevant for events in `cache.json`, `pipeline.json`, and virtual-memory files because only two generic counters mean many user-selected combinations will require multiplexing unless fixed counters can be used.

## Risks
If the fixed or generic counter counts are wrong, perf may present misleading scheduling expectations or generate incorrect metadata. The small generic-counter count is also an operational risk for analysis: users comparing many aliases at once may see multiplexed scaled counts rather than simultaneously measured counters.

## Test Signals
Validate JSON syntax and generated perf metadata. On Silvermont hardware or emulation with matching PMU support, `perf stat` with more than two generic events should reveal multiplexing behavior, while fixed events such as retired instructions and unhalted cycles should use fixed counter paths where supported.
