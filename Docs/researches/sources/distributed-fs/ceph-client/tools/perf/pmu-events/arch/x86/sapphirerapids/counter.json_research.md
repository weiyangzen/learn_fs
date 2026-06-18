# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/counter.json

## Purpose
`counter.json` declares the number of programmable and fixed counters available for each Sapphire Rapids PMU unit known to perf. It is a compact capacity table with 16 objects. The core entry declares 4 fixed counters and 8 generic counters, while uncore units such as `PCU`, `IIO`, `iMC`, `M2M`, `UPI`, `CHA`, `CXLDP`, `MCHBM`, and others declare their generic counter counts.

## Important APIs, types, and schema fields
Each object has `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The schema is consumed as PMU metadata rather than an event list. `Unit` names must match perf's PMU naming/model vocabulary, and the numeric fields are stored as strings consistent with other pmu-events JSON files.

## Control flow and integration
The build-time event generator reads this file alongside the model's event JSON. Runtime perf code can use the generated metadata to reason about how many events can be scheduled on a PMU class before multiplexing or constraint failures. The file does not define encodings; it constrains capacity for events defined in this directory and other Sapphire Rapids uncore JSON files.

## State and persistence behavior
This is static hardware topology metadata. It persists the expected counter inventory for Sapphire Rapids PMUs: `core` has 8 generic and 4 fixed counters; most listed uncore boxes have 4 generic counters; `IRP` and `UBOX` have 2; `CXLCM` has 8. Runtime counter allocation and multiplexing state belongs to perf and the kernel PMU drivers.

## Dependencies
The table depends on kernel/perf PMU unit names and Sapphire Rapids uncore hardware definitions. It integrates with all Sapphire Rapids event files because their `Counter` fields must be meaningful relative to these counts. It also informs user-facing event scheduling expectations for CXL, HBM, mesh, memory controller, PCIe, power-control, and core PMUs.

## Risks and edge cases
Wrong counter counts cause scheduler confusion: perf may accept impossible groups, over-multiplex, reject valid groups, or display misleading PMU capacity. Unit-name drift is also risky; a typo creates orphan metadata that generated tables may not associate with the intended PMU. Because values are strings, tests should catch nonnumeric text and accidental integer/string shape changes.

## Test signals
Validate JSON syntax and that each row has exactly the three expected keys. Compare unit names against Sapphire Rapids uncore event files and generated PMU tables. On hardware, `perf list` plus grouped `perf stat` experiments can reveal whether counter counts match actual scheduling constraints, especially for `core`, `CHA`, `iMC`, `CXLCM`, and `UBOX`.
