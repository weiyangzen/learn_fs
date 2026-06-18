# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/cache.json

## Purpose
This is the large Nehalem EX cache and offcore-cache PMU table. It contains 319 aliases spanning L1D line replacement and MESI-state accesses, L1I hits/misses/stalls, L2 data requests, lines in/out, L2 request/transaction/write categories, longest-latency cache references, retired load/cache-hit PEBS events, retired memory latency threshold events, offcore response matrices, lock cycles, super-queue pressure, and store-block events.

## Important APIs, Types, And Fields
Objects follow the perf event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, and `SampleAfterValue`. This file also uses `PEBS` for 23 precise retired memory events and `MSRIndex`/`MSRValue` for 218 threshold/offcore events. Offcore response aliases use event `0xB7`, `UMask: 0x1`, counter `2`, and `MSRIndex: 0x1A6`; the `MSRValue` encodes request class and response location. Memory latency threshold aliases use `MSRIndex: 0x3F6`, event `0xB`, `UMask: 0x10`, counter `3`, and threshold values from 0 through 32768.

## Control Flow
The JSON is declarative. `jevents.py` reads each object, emits generated PMU tables, and perf later programs counters using the encoded event selector. The special flow for this file is offcore and threshold programming: when a user selects an alias like `OFFCORE_RESPONSE.DEMAND_DATA_RD.REMOTE_CACHE_HITM`, perf must program the event plus the model-specific MSR filter, not just `EventCode`/`UMask`.

## State And Persistence
The file persists a static catalog of cache measurements. It has no mutable state, but its `MSRValue` fields persist model-specific filter bitmasks in generated data. Most events use `SampleAfterValue: 2000000`. PEBS retired load events such as `MEM_LOAD_RETIRED.L1D_HIT`, `L2_HIT`, `LLC_MISS`, and latency-threshold events influence precise sampling behavior.

## Dependencies And Integration Points
The file depends on Nehalem EX uncore/offcore filter semantics, generic x86 PMU counters, and perf support for `MSRIndex`/`MSRValue`. It integrates with `perf list` category display, event alias resolution, generated `pmu-events.c`, and kernel PMU programming for offcore response events. It is closely related to `memory.json`, which contains a narrower DRAM/LLC-miss offcore subset.

## Risks
The highest risk is incorrect offcore filter masks: many aliases share the same visible event selector, so only `MSRValue` differentiates local/remote cache, DRAM, IO/CSR/MMIO, HIT/HITM, demand, prefetch, RFO, and code/data forms. Counter constraints are also significant because offcore aliases are bound to counter 2 and latency thresholds to counter 3. A generated table may compile while measuring the wrong request class. Duplicated matrix entries also raise copy/paste drift risk.

## Test Signals
Run JSON validation, `jevents.py` generation, and generated PMU event tests. Inspect generated rows for at least one L1/L2 plain event, one PEBS retired load event, one latency-threshold event using MSR `0x3F6`, and one offcore response event using MSR `0x1A6`. On capable hardware or emulation, `perf stat -e` smoke tests should include an offcore alias to catch MSR programming issues.
