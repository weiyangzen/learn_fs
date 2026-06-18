# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/counter.json

Purpose: declares Nehalem EP PMU counter inventory for the `core` unit: four fixed counters and four generic programmable counters.

Important APIs/types/functions: this is a one-row JSON metadata file with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. It is consumed by perf PMU event tooling as platform capability metadata rather than as a countable event. There are no functions or event encodings.

Control flow: build tooling reads the metadata alongside event files and can use it to describe available counters in generated PMU tables or validation logic. Runtime perf scheduling ultimately depends on kernel PMU capabilities, but this file documents the expected Nehalem EP counter topology for the event catalog.

State and persistence: static platform metadata only. It does not create runtime state or persist measurements.

Dependencies and integration points: integrates with the rest of `arch/x86/nehalemep` event files and the perf PMU event generator. The declared generic/fixed counts provide context for counter constraints in cache, memory, frontend, floating-point, and other event files.

Risks: an incorrect counter count would mislead generated metadata and humans reasoning about event scheduling. The values are strings, matching surrounding schema conventions; tooling must parse or preserve them correctly. This file has no `EventName`, so consumers must tolerate metadata rows without event aliases.

Test signals: JSON validation and a generator run that confirms metadata-only rows do not require `EventName`. Cross-check with generated tables and Nehalem EP PMU scheduling behavior where available.
