# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/metricgroups.json

Purpose: Provides 124 human-readable descriptions for Ivy Town metric group names used by `ivt-metrics.json`. This file is metadata for organizing and explaining perf metrics, especially topdown analysis groups and issue categories.

Important APIs/types/functions: Unlike most PMU event files, this JSON file is an object mapping group name to description. Keys include broad groups such as `Backend`, `Frontend`, `MemoryBound`, `MemoryBW`, `Offcore`, `Power`, `Summary`, and `SMT`; topdown levels `TopdownL1` through `TopdownL6`; mirrored internal groups like `tma_L1_group`; contributing-category groups like `tma_backend_bound_group`; and issue tags such as `tma_issueBW`, `tma_issueFB`, `tma_issueTLB`, and `tma_issueSyncxn`.

Control flow: Perf loads metric group descriptions when displaying or documenting metric groups. `ivt-metrics.json` entries list semicolon-separated `MetricGroup` values; those group IDs are resolved here for user-facing descriptions. The file does not schedule events or evaluate formulas.

State and persistence: Static descriptive metadata only. It persists labels and descriptions in the repository and has no runtime mutable state.

Dependencies/integration: Depends on group names matching the `MetricGroup` tokens in `ivt-metrics.json`. It also reflects naming from Intel's Top-down Microarchitecture Analysis spreadsheet, so consistency with imported metric definitions matters. Perf UI/help output depends on this file for readable grouping context.

Risks: Missing or misspelled group keys do not necessarily break metric computation, but they degrade discoverability and may leave groups undocumented. Because this file is object-shaped while event files are arrays, tooling that assumes arrays will fail. Generic descriptions repeated across many spreadsheet-derived groups are useful but not very specific, so users may need metric-level descriptions for interpretation.

Test signals: Validate JSON object shape, unique keys, and string descriptions. Cross-check every `MetricGroup` token from `ivt-metrics.json` against this object, allowing only deliberate built-in or legacy exceptions. UI tests should confirm `perf list --metricgroups` or equivalent help paths show these descriptions.
