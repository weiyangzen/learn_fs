# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/decode.json

Purpose: Defines 23 Zen 6 decode, op-source, and dispatch-stall PMU events used for frontend and backend dispatch-slot analysis.

Important APIs/types/functions: Uses `EventName`, `EventCode`, `UMask`, and `BriefDescription`. Families include `de_op_queue_empty`, `de_src_op_disp.*`, `de_dis_ops_from_decoder.*`, dynamic token stall parts 1 and 2, `de_no_dispatch_per_slot.*`, and `de_additional_resource_stalls.dispatch_stalls`.

Control flow: Perf exposes these aliases. Zen 6 pipeline metrics consume `de_no_dispatch_per_slot.*` and `de_src_op_disp.all`; recommended macro-op dispatch metrics consume `de_src_op_disp.all`.

State and persistence: No runtime state. The persistent API is the Zen 6 naming for decoder source and dispatch stalls.

Dependencies and integration: Integrates with load-store, execution, branch-prediction, and pipeline metric files. Compared with Zen 5, token stalls are enumerated as `int_sq0` through `int_sq5` and `ret_q`, with an aggregate `all`.

Risks: Renaming from Zen 5 spellings such as `any_fp_dispatch` to `any_fp` and `retq` to `ret_q` can break reused tooling. Dynamic token stall categories overlap and should be interpreted as attribution signals rather than exclusive buckets.

Test signals: Validate pmu-events generation, `perf list de_`, pipeline metric evaluation, and workloads that stress decoder bandwidth, op-cache supply, SMT contention, integer scheduler tokens, and retire queue pressure.
