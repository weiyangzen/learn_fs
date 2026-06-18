# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/frontend.json

## Purpose

This file defines 29 HaswellX core frontend events. It covers branch-address clears, DSB-to-MITE switch penalties, instruction-cache hits/misses/stalls, IDQ delivery by DSB/MITE/microcode sequencer, and frontend under-delivery cycles for top-down analysis.

## Important APIs, Types, And Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and sometimes `PublicDescription`. Families include `BACLEARS.ANY`, `DSB2MITE_SWITCHES.PENALTY_CYCLES`, four `ICACHE` aliases, 17 `IDQ` aliases, and six `IDQ_UOPS_NOT_DELIVERED` aliases.

Several aliases intentionally share event selector and mask values while representing different derived interpretations, such as DSB cycles versus DSB uops or MITE cycles versus MITE uops. Top-down frontend metrics use these names to distinguish decode-source coverage, microcode sequencer behavior, and delivery shortfall.

## Control Flow

At build time, `jevents.py` emits these entries into the HaswellX core event table. At runtime, perf programs the selected frontend counters or expands metrics that reference them. The aliases support both direct `perf stat -e` analysis and derived frontend-bound, fetch-bandwidth, fetch-latency, DSB, MITE, and microcode-sequencer metrics.

## State And Persistence Behavior

The file stores static alias definitions and sample periods. Instruction-cache state, decode-source usage, IDQ occupancy, and frontend delivery shortages are hardware/runtime behavior. No state is mutated or persisted by the JSON itself.

## Dependencies And Integration Points

Dependencies include HaswellX model matching, perf PMU event generation, generated alias lookup, top-down metric formulas, frontend performance workflows, and event semantics for DSB, MITE, LSD, and microcode sequencer paths. It overlaps conceptually with Haswell pipeline metrics but is HaswellX-specific.

## Risks And Edge Cases

Shared encodings with different names can confuse validation that looks only at event selector/mask pairs. The difference between cycles, uops, occurrences, and penalties is central; using the wrong alias in a formula changes the unit of analysis. Some frontend events are sensitive to SMT, instruction-cache footprint, branch predictor behavior, and microcode assists, so synthetic tests need controlled workloads.

## Test Signals

Validate JSON and generated aliases. Runtime tests should include instruction-cache footprint stress, branch-indirect or branch-clear workloads, decode-source comparisons that fit in DSB versus force MITE decode, and microcode-heavy instruction sequences. `perf list` should expose representative `ICACHE.*`, `IDQ.*`, and `IDQ_UOPS_NOT_DELIVERED.*` aliases for HaswellX.
