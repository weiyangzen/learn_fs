# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/counter.json

Purpose: declares the Westmere-EP SP core counter topology: one `core` unit with four fixed counters and four generic programmable counters.

Important APIs/types/functions: this file uses the counter-description schema rather than event rows: `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. It does not define `EventName`, `EventCode`, or `UMask`.

Control flow: when perf's PMU event tooling consumes architecture data, this descriptor documents counter capacity for the model directory. Runtime event scheduling still occurs in perf and the kernel PMU driver; this file provides model metadata rather than aliases.

State and persistence: static metadata only. It does not create runtime counters; it records the expected hardware counter counts that scheduling and documentation can rely on.

Dependencies and integration points: tied to the `westmereep-sp` event directory selected for CPUID `GenuineIntel-6-25`. It contextualizes other SP topic files: many aliases list generic counters `0,1,2,3`, and fixed-counter aliases in `pipeline.json` assume fixed counter availability.

Risks: if the declared counts do not match hardware or perf scheduler assumptions, event group feasibility and diagnostic output can be misleading. Because this is a one-row file, schema drift is easy to overlook in broad JSON validators focused on `EventName`.

Test signals: JSON syntax validation, generation tooling accepting a non-event JSON record, and runtime checks that fixed-counter aliases and four-way generic event groups schedule as expected on matching hardware.
