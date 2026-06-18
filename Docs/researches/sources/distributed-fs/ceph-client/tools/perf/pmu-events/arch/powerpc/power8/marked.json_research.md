# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/marked.json

## Purpose

This file defines 132 POWER8 raw PMU events for marked or sampled instruction behavior. It covers marked branch completion, marked load sourcing and latency cycles, marked data ERAT/DTLB misses by page size, marked data-side PTE sourcing, fabric response outcomes for stores, marked instruction lifecycle events, marked cache reload intervals, load miss exposure, store completion/drain timing, marked run cycles, and synchronization marker reasons.

## APIs, types, and schema

The schema is `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`. Event names are mostly prefixed with `PM_MRK_`, plus marker synchronization events such as `PM_SYNC_MRK_BR_LINK`, `PM_SYNC_MRK_BR_MPRED`, `PM_SYNC_MRK_FX_DIVIDE`, `PM_SYNC_MRK_L2HIT`, `PM_SYNC_MRK_L2MISS`, `PM_SYNC_MRK_L3MISS`, and `PM_SYNC_MRK_PROBE_NOP`. Pairs such as `PM_MRK_DATA_FROM_L2` and `PM_MRK_DATA_FROM_L2_CYC` expose both occurrence and duration.

## Control flow and integration

Perf generation adds these marked events to the POWER8 PMU table. At runtime, they are used for sampled/marked instruction analysis where the PMU follows selected instructions and attributes latency, sourcing, stalls, or completion behavior. The control model is declarative but semantically tied to PMU marking configuration and sampling behavior.

## State and persistence

The JSON is static. The persistent output is a large set of generated event identifiers and descriptions. Runtime marking state is owned by the PMU and perf event configuration, not by this file, but these entries define the names that expose that state.

## Dependencies

Dependencies include POWER8 marked-event PMU semantics, fabric response definitions, cache and memory topology, ERAT/DTLB page-size classifications, store pipeline timing, and perf's raw event generator. Integration points are generated event tables, direct perf event selection, and any higher-level marked-event analysis tools.

## Risks

This is a dense, high-risk metadata file because many names differ only by source, coherency state, or `_CYC` suffix. Copy/paste mistakes can swap event codes or descriptions while still passing JSON syntax checks. Users may confuse marked events with aggregate events from `cache.json` or `memory.json`. Marked events also require correct sampling setup; direct counts without understanding PMU marking can be misleading.

## Test signals

Validation should include JSON parsing, event-name and event-code uniqueness, generated PMU build, and targeted runtime tests for representative marked data source, marked branch, marked DTLB/DERAT, and marked store events. Review tests should ensure `_CYC` duration events are paired correctly with non-cycle events where expected.
