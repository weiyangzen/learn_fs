# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/frontend.json

Purpose: defines three Nehalem EP frontend decode events: decoded macro-instructions, decoded macro-fused instructions, and decoded two-uop instructions.

Important APIs/types/functions: static descriptors with `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Events are `MACRO_INSTS.DECODED` (`0xD0/0x1`), `MACRO_INSTS.FUSIONS_DECODED` (`0xA6/0x1`), and `TWO_UOP_INSTS_DECODED` (`0x19/0x1`), all available on counters `0,1,2,3`.

Control flow: perf generation converts the JSON rows to aliases. Runtime perf programs the selected event to count decode-path behavior during a workload, allowing users to compare instruction decode volume with retired instruction and uop activity.

State and persistence: no source-level state. Counts live in core PMU counters during perf measurement and may be stored in perf output.

Dependencies and integration points: depends on Nehalem EP PMU event encoding and perf PMU event generation. Integrates with pipeline, cache, and floating-point events when diagnosing frontend pressure or macro-fusion effectiveness.

Risks: the event family is small but semantically specific; macro-fusion counts are not the same as total fused-domain uops. If descriptions are used in generated help text, stale wording can mislead users about decode pipeline behavior. Counter availability is broad, but concurrent use with other events still competes for four generic counters.

Test signals: JSON validation, generated alias presence, `perf list` checks, and microbenchmarks with branch/compare patterns that should alter macro-fusion counts. Compare decoded instruction counts with retired instruction counts for sanity.
