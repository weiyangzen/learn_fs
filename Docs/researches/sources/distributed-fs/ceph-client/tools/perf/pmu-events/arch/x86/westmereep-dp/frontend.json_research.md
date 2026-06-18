# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/frontend.json

Purpose: provides the small Westmere-EP DP frontend-topic table with three decode-related aliases: decoded macro-instructions, decoded macro-fusions, and decoded two-uop instructions.

Important APIs/types/functions: each record uses `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. The events are `MACRO_INSTS.DECODED`, `MACRO_INSTS.FUSIONS_DECODED`, and `TWO_UOP_INSTS_DECODED`. They become `struct pmu_event` rows after `jevents.py` processing.

Control flow: `jevents.py` recursively loads topic JSON files for the `westmereep-dp` directory, assigns the topic from the filename, normalizes names to lowercase aliases, and writes generated event tables. Runtime perf table selection comes from `arch/x86/mapfile.csv`, where `GenuineIntel-6-2C` maps to `westmereep-dp`.

State and persistence: no mutable state. The persisted values are raw hardware select/umask tuples and default sampling periods. perf turns them into event encodings when a user requests the alias.

Dependencies and integration points: depends on the x86 PMU event schema and the frontend event definitions being valid for Westmere-EP DP. Integrates with frontend bottleneck analysis and can be combined with pipeline counters such as `uops_decoded.*`.

Risks: because the file is tiny, omissions are easy to miss: it covers decode counts but not instruction-cache or length-decoder stalls, which are in other topic files. Bad `SampleAfterValue` or event code values would affect sampling defaults for `perf record`.

Test signals: valid JSON parsing, generated `pmu-events.c` presence, `perf list frontend`/`perf list macro_insts`, and direct event scheduling on matching hardware. Cross-checking with `pipeline.json` helps detect name drift between decode and uop counters.
