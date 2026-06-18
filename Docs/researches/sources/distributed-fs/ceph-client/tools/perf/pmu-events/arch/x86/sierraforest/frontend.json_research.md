# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/frontend.json

## Purpose

This 13-entry Sierra Forest frontend event table defines aliases for branch-address clears, frontend-retired stall attribution, instruction-cache accesses/misses, and micro-sequencer busy cycles. It supports topdown frontend-bound analysis and instruction-fetch troubleshooting.

## Important APIs, Types, and Data

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and optional `PublicDescription`. The `FRONTEND_RETIRED.*` family uses event `0xc6` to tag retired instructions following frontend-bound behavior, with categories for branch detect, branch resteer, CISC/micro-sequencer flows, decode, instruction cache, ITLB miss, predecode, and other. `BACLEARS.ANY` uses event `0xe6`, `ICACHE.*` uses event `0x80`, and `MS_DECODED.MS_BUSY` uses event `0xe7`.

## Control Flow

Perf exposes these aliases as core PMU events on generic counters `0-7`. Runtime analysis usually starts with aggregate frontend-bound or topdown events, then uses these aliases to separate branch redirection, decode, instruction-cache, ITLB, micro-sequencer, and residual frontend costs. The table itself has no code flow; the control path is perf alias resolution and counter programming.

## State and Persistence Behavior

The file persists event encodings and sample defaults. Runtime counts are per perf session and per selected CPU/thread scope. `FRONTEND_RETIRED` events are attribution/tagging signals tied to retired instructions after frontend bubbles, not direct raw counts of each root-cause occurrence. `BACLEARS` and `ICACHE` events count different domains and should be normalized before comparison.

## Dependencies and Integration Points

This table integrates with Sierra Forest topdown metric groups, `pipeline.json` topdown slots, `virtual-memory`-style ITLB signals from other architectures, and perf frontend profiling workflows. It depends on core PMU support for frontend-retired tagging and instruction-cache events.

## Risks

Frontend attribution events can be misread as exact causal counts rather than sampled/tagged retirement signals. Branch detect/resteer, predecode, and other categories may overlap conceptually with topdown slot events in `pipeline.json`, so formulas need documented semantics. Instruction-cache miss behavior is workload and code-layout sensitive, and sampling can perturb tiny loops. Metrics should avoid assuming one frontend category fully partitions all stalls unless Intel's model says so.

## Test Signals

Validation should include JSON parsing, alias listing, and smoke tests with branch-heavy code, large instruction footprints, ITLB pressure, decode-heavy instruction streams, and microcoded instruction loops. Topdown tests should verify frontend-bound formulas resolve both this file's `FRONTEND_RETIRED.*` aliases and `pipeline.json` slot aliases.
