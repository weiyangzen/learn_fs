# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/other.json

## Purpose

`amdzen3/other.json` defines 17 Zen 3 decode/dispatch and scheduler-resource events that do not fit cleanly in cache, memory, core, or floating-point categories. These counters expose empty micro-op queues, decoder dispatch classes, and dispatch token stalls.

## Important records and schema

Entries use `EventName`, `EventCode`, optional `UMask`, and `BriefDescription`.

Important event families include:

- `de_dis_uop_queue_empty_di0`: cycles where the micro-op queue is empty.
- `de_dis_cops_from_decoder.disp_op_type.any_integer_dispatch` and `.any_fp_dispatch`: integer and FP ops dispatched from decoder.
- `de_dis_dispatch_token_stalls1.*`: first group of dispatch token stalls, including FP flush recovery, FP scheduler/resource stalls, FP register file stalls, taken branch buffer stalls, integer scheduler miscellaneous stalls, store queue stalls, load queue stalls, and integer physical register file stalls.
- `de_dis_dispatch_token_stalls2.*`: second group of token stalls, including retire queue, AGSQ, and integer scheduler queue 0-3 token stalls.

## Control flow and integration

The file is generated into core PMU aliases by the standard perf PMU event pipeline. `amdzen3/recommended.json` references the decoder dispatch aliases in `macro_ops_dispatched`; users can combine token-stall aliases with cache/memory/core counters to diagnose backend dispatch bottlenecks.

## State and persistence

The file has no mutable state. Its durable behavior is the mapping from dispatch stall names to hardware event codes and masks.

## Dependencies

Dependencies include AMD Zen 3 decode/dispatch PMU definitions and perf's event schema. Metric expressions depend on the exact `de_dis_cops_from_decoder.*` names.

## Risks

Dispatch token events count cycles where a valid dispatch group is stalled and may also count cycles when a thread is not selected but would have stalled. Users may overinterpret them as exclusive bottleneck buckets. Renaming decoder dispatch aliases breaks `macro_ops_dispatched`.

## Test signals

Validate JSON and PMU generation. Metric tests should resolve `macro_ops_dispatched`. Hardware sanity checks can compare token-stall counters under queue-pressure or FP-heavy workloads, and verify aliases appear in `perf list` on Zen 3.
