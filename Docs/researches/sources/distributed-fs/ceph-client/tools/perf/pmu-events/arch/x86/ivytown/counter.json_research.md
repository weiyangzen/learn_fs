# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/counter.json

Purpose: Declares the Ivy Town PMU counter inventory by PMU unit. This file informs perf tooling how many fixed and generic counters exist for the core and each uncore unit.

Important APIs/types/functions: The JSON array contains 10 unit records with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. It lists `core` as 3 fixed counters and 4 generic counters, and uncore units `CBOX`, `HA`, `iMC`, `PCU`, and `QPI` as 4 generic counters each. `IRP` and `UBOX` have 2 generic counters, while `R3QPI` has 3. All uncore units list zero fixed counters.

Control flow: Perf PMU event table generation and validation can use this metadata to understand event scheduling capacity and unit capabilities. Runtime event grouping, multiplexing, and error reporting depend on the kernel PMU driver and perf's scheduler, but this file documents the expected Ivy Town hardware shape for generated metadata.

State and persistence: Static architecture metadata only. It has no event names and no runtime state. The persisted state is the counter-count contract for Ivy Town units.

Dependencies/integration: Integrates with all Ivy Town event files by providing the available counter context for `core`, CBOX, HA, iMC, IRP, PCU, QPI, R2PCIe, R3QPI, and UBOX events. It depends on unit names matching `Unit` fields in uncore event JSON files and perf's unit naming conventions.

Risks: If unit names drift from event files or kernel PMU names, generated metadata becomes misleading. Counter counts can vary by SKU or kernel exposure, so this file should be treated as model metadata rather than live discovery. Incorrect counts can cause overly optimistic grouping or missed multiplexing warnings.

Test signals: JSON validation should ensure every record has numeric string counts and unique `Unit` values. Cross-file tests should verify all Ivy Town `Unit` values used by event files appear here or are deliberately excluded. Runtime tests should compare perf-detected PMU counter capabilities against the expected model where Ivy Town hardware is available.
