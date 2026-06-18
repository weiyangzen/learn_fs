# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/memory.json

## Purpose

This 13-entry Sierra Forest memory event table focuses on load-head stalls, memory-ordering clears, misaligned page splits, and offcore demand-read/RFO outcomes. It is narrower than `cache.json` and provides memory execution and NUMA/DRAM response signals for perf.

## Important APIs, Types, and Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, and offcore `MSRIndex`/`MSRValue`. `LD_HEAD.*` uses event `0x05` for oldest-load stall cycles at retirement, split into any, L1-bound, L1 miss, page walk, store-address, and other causes. `MACHINE_CLEARS.MEMORY_ORDERING` uses event `0xc3`, `MISALIGN_MEM_REF.*_PAGE_SPLIT` uses `0x13`, and `OCR.*` events use `EventCode 0xB7`, `UMask 0x1`, and MSRs `0x1a6,0x1a7` for L3 miss, local DRAM, remote DRAM, and RFO L3-miss filters.

## Control Flow

Perf programs regular core counters for load-head, machine-clear, and misalignment aliases. For `OCR.*`, perf also programs offcore response MSRs with the listed filter value before enabling the event. Users combine this file with cache and pipeline events to determine whether backend stalls come from load-buffer head blocking, page walks, store-address conflicts, misaligned accesses, ordering nukes, or remote/local DRAM responses.

## State and Persistence Behavior

The persistent state is the alias-to-encoding table and offcore filter values. Runtime state includes counter values and temporary offcore MSR programming for the perf session. Load-head events count cycles with the oldest load stalled at retirement and are not simple retired-load counts. Offcore response filters are shared hardware state managed by perf, so concurrent offcore users must be scheduled carefully.

## Dependencies and Integration Points

This file integrates with perf's core PMU and offcore response handling, `cache.json` load/cache events, `pipeline.json` backend topdown events, and NUMA/local-versus-remote memory analysis. It depends on kernel support for programming the offcore response MSRs and on accurate Sierra Forest response encodings.

## Risks

Offcore filters are the highest-risk data because a wrong `MSRValue` silently changes the memory-response class. Load-head stall categories can overlap conceptually with broader topdown backend-bound categories, so metric formulas need careful normalization. Misaligned page-split events are rare in normal workloads and may need targeted tests. Remote DRAM counts require a multi-socket or otherwise remote-memory setup; on single-socket systems they may be zero by design.

## Test Signals

Tests should parse the JSON, expose aliases, and compare generated offcore MSR programming to reference encodings. Runtime smoke tests should include pointer-chasing, page-walk-heavy loads, store-address conflict patterns, page-split load/store cases, and local versus remote NUMA memory placement. Metrics should verify `LD_HEAD` cycle counts are normalized against cycles or slots, not retired loads.
