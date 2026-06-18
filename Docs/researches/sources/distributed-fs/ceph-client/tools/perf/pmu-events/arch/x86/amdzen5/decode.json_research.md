# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/decode.json

Purpose: Defines 19 Zen 5 decoder and dispatch PMU events used to diagnose frontend supply, op-cache versus x86-decoder source, dispatch stalls, and empty dispatch slots.

Important APIs/types/functions: The file is a perf PMU event table using `EventName`, `EventCode`, `UMask`, and `BriefDescription`. Key families are `de_op_queue_empty`, `de_src_op_disp.*`, `de_dis_ops_from_decoder.*`, `de_dispatch_stall_cycle_dynamic_tokens_part1.*`, `de_dispatch_stall_cycle_dynamic_tokens_part2.*`, `de_no_dispatch_per_slot.*`, and `de_additional_resource_stalls.dispatch_stalls`.

Control flow: Perf's pmu-events parser turns these objects into named CPU events. Zen 5 pipeline and recommended metrics consume them, especially `de_no_dispatch_per_slot.no_ops_from_frontend`, `de_no_dispatch_per_slot.backend_stalls`, `de_no_dispatch_per_slot.smt_contention`, and `de_src_op_disp.all`.

State and persistence: No runtime state is stored here. The durable state is the event-name contract and raw event/umask encodings for decoder-source and dispatch-stall attribution.

Dependencies and integration: Integrates with the core CPU PMU, pipeline topdown-style metrics, and recommended macro-op dispatch metrics. Its event names must remain aligned with formula references in `pipeline.json` and `recommended.json`.

Risks: Zen 5 uses names such as `any_fp_dispatch`, `any_integer_dispatch`, `al_tokens`, `ag_tokens`, and `retq` that differ from Zen 6 spellings, so cross-generation copy edits can silently break metric references or user scripts. Dynamic-token stall events are overlapping categories and should not be summed as disjoint causes without documentation.

Test signals: Check pmu-events generation, `perf list de_`, pipeline metric resolution, and targeted workloads that stress frontend starvation, op cache, SMT contention, load/store queue tokens, and retire queue stalls.
