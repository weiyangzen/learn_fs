# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/frontend.json

Purpose: supplies three Westmere-EP SP frontend decode aliases for macro-instruction decode volume, macro-fusion decode count, and two-uop decoded instructions.

Important APIs/types/functions: records are `MACRO_INSTS.DECODED`, `MACRO_INSTS.FUSIONS_DECODED`, and `TWO_UOP_INSTS_DECODED`, each with `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. `jevents.py` converts them to `struct pmu_event` entries.

Control flow: the build traverses the SP model directory, reads the frontend topic JSON, and writes generated C event tables. At runtime, perf selects the SP table for CPUID `GenuineIntel-6-25` and exposes lowercase aliases to command-line event parsing.

State and persistence: static source data only. Active counter state is held by perf/kernel PMU while recording or counting.

Dependencies and integration points: complements `pipeline.json` decode and uop stall rows and `cache.json` instruction fetch rows. It is useful for frontend throughput and macro-fusion analysis.

Risks: narrow scope may be mistaken for complete frontend coverage. Instruction-cache misses, length decoder stalls, instruction queue writes, and uop decode stalls live in other topic files. Any schema change in perf event JSON handling would affect this small file the same as larger event tables.

Test signals: `jq empty`, generated alias inspection, `perf list macro_insts`, and workloads that vary branch/fusion behavior or instruction mix.
