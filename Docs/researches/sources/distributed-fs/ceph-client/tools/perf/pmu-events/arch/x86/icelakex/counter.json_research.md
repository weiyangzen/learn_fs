# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/counter.json

Purpose: Declares counter inventory for Ice Lake Xeon PMU units. Unlike the event-definition files, this table describes how many fixed and generic counters exist for the core PMU and each uncore PMU unit so perf can expose capacity metadata for scheduling and discovery.

Important schema fields and entries: Each object uses `Unit`, `CountersNumFixed`, and `CountersNumGeneric`; it intentionally has no `EventName`. The file lists 11 units: `core` with 4 fixed and 8 generic counters, `CHA`, `IIO`, `M2M`, `UPI`, `M2PCIe`, `M3UPI`, and `PCU` with 4 generic counters, `IRP` and `UBOX` with 2 generic counters, and `iMC` with 1 fixed plus 4 generic counters. `UBOX` stores `CountersNumFixed` as numeric `1` while most other counts are strings, so consumers must tolerate both JSON number and string forms.

Control flow: During PMU event generation, this file is read as metadata rather than as an event alias list. `jevents.py` and the generated PMU tables use `Unit` naming rules to associate metadata with PMU names: `core` maps to the default core PMU, while unknown units map by convention to uncore PMU names such as `uncore_cha`, `uncore_iio`, or `uncore_pcu`. Runtime perf can then present and reason about unit counter capacities alongside model-specific event tables.

State and persistence behavior: The file is static metadata. It has no runtime state, but its values persist into generated perf tables and affect user expectations about groupability and available counters. Incorrect capacities can make valid groups look impossible or make impossible groups appear schedulable until kernel PMU constraints reject them.

Dependencies and integration points: Depends on the PMU event metadata schema and on `jevents.py` unit-to-PMU naming. It integrates with all `icelakex` event categories because event tables reference the same PMU units, and with perf list/introspection paths that expose counter counts.

Risks: Mixed numeric/string count representation is a schema consistency risk for strict validators. Unit spelling is ABI-like: changing `iMC`, `M2PCIe`, or `M3UPI` casing can alter generated uncore PMU names. The file does not specify per-event constraints, so it is capacity metadata only and must not be used as a complete scheduler model.

Test signals: Validate the JSON array has 11 objects and no accidental `EventName` keys. Build perf with jevents enabled and confirm counter metadata is accepted despite mixed number/string values. Cross-check against Ice Lake Xeon PMU documentation or kernel uncore PMU registration names, especially for `iMC`, `UBOX`, `M2PCIe`, and `M3UPI`.
