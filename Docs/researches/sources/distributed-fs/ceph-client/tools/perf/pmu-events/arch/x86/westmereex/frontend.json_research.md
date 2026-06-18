# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/frontend.json

Purpose: declares three Westmere EX frontend decode PMU events: decoded macro-instructions, decoded macro-fusions, and decoded two-uop instructions.

Important APIs/types/functions: the rows use `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`. All three use generic counters `0,1,2,3`, `UMask` `0x1`, and a default sample-after value of `2000000`.

Control flow: no local execution. The rows are consumed by perf's PMU event generation and later selected by symbolic names such as `MACRO_INSTS.DECODED` or `TWO_UOP_INSTS_DECODED`.

State and persistence: static event metadata only. Runtime perf sessions program counters based on these rows; no persistent state is modified.

Dependencies: depends on Westmere EX frontend event encodings and the perf PMU JSON schema. It is intentionally narrow and complements broader branch, uop, and instruction queue coverage in `pipeline.json`.

Integration points: integrates with `perf list` and perf event lookup for frontend decode analysis. Higher-level metrics may combine these frontend counts with instruction-retired or uop events from `pipeline.json` to reason about decode efficiency and macro-fusion behavior.

Risks: because the file is tiny, accidental deletion or renaming of one row would remove a substantial fraction of Westmere EX frontend coverage. The events have similar field shapes, so copy/paste changes to `EventCode` or `EventName` are the main risk.

Test signals: JSON parse, exactly three rows, unique names, all required fields present, and successful generated perf event listing for the three names.
