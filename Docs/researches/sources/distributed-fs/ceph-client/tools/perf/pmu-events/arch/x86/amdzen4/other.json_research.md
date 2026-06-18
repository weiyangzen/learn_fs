# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen4/other.json

## Purpose

`amdzen4/other.json` defines 23 Zen 4 frontend/decode/dispatch and pipeline-support events. It exposes operation source counts, no-dispatch slot reasons, token stalls, op-queue empty cycles, and resync/non-cacheable redirects.

## Important records and schema

Entries use `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`.

Important families include:

- `resyncs_or_nc_redirects`: pipeline restart/resync or non-cacheable redirect count used by bad-speculation split metrics.
- `de_op_queue_empty`: op queue empty cycles.
- `de_src_op_disp.*`: macro-ops dispatched by decoder, op cache, loop buffer, and all sources.
- `de_dis_ops_from_decoder.*`: decoder dispatch classes for integer and FP dispatch.
- `de_no_dispatch_per_slot.*`: no-dispatch slots from frontend, backend stalls, and SMT contention.
- `de_dis_dispatch_token_stalls1.*` and `de_dis_dispatch_token_stalls2.*`: dispatch token stalls from FP resources, branch buffers, integer scheduler resources, store/load queues, retire queue, AGSQ, and scheduler queues.

## Control flow and integration

The file feeds generated core PMU aliases. `amdzen4/pipeline.json` depends on `de_no_dispatch_per_slot.*`, `de_src_op_disp.all`, and `resyncs_or_nc_redirects`. `amdzen4/recommended.json` uses `de_src_op_disp.all` for `macro_ops_dispatched`.

## State and persistence

There is no mutable state. Persistent behavior is the mapping of dispatch-source and no-dispatch categories to event masks. These counters provide denominators and classifiers for top-down pipeline metrics.

## Dependencies

Dependencies include AMD Zen 4 decode/dispatch PMU definitions, recommended metrics, and pipeline metrics.

## Risks

Top-down metrics depend on these events being semantically compatible with a six-slot dispatch model. Token stall categories may overlap or be non-exclusive in ways users should not treat as exact percentages unless formulas account for them. Renaming `de_no_dispatch_per_slot.*` or `de_src_op_disp.all` breaks pipeline formulas.

## Test signals

Validate JSON and generated aliases. Run metric parser tests for all `pipeline.json` formulas. Hardware checks should compare frontend-bound, backend-bound, SMT contention, and dispatch-source counts under instruction-cache pressure, memory stalls, single-threaded, and SMT workloads.
