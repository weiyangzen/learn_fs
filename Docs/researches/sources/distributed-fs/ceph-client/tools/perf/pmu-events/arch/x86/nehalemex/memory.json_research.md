# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/memory.json

## Purpose
This file defines 67 Nehalem EX memory-oriented offcore response aliases. It focuses on LLC misses and DRAM locality: `ANY_DRAM`, `ANY_LLC_MISS`, `LOCAL_DRAM`, and `REMOTE_DRAM` variants across request classes such as data reads, instruction fetches, all requests, RFOs, core writebacks, demand data, demand ifetch, demand RFO, prefetch data, prefetch ifetch, and prefetch RFO.

## Important APIs, Types, And Fields
Each alias uses `EventCode: 0xB7`, `UMask: 0x1`, `Counter: 2`, `MSRIndex: 0x1A6`, and a request/response-specific `MSRValue`. The objects also include `EventName`, `BriefDescription`, and `SampleAfterValue`. Unlike `cache.json`, this file has no `PEBS`; it is entirely offcore MSR-filter metadata.

## Control Flow
The file is declarative. Build-time `jevents.py` emits generated rows that include both the visible PMU event selector and the model-specific offcore filter. Runtime perf must program the offcore response MSR as well as the counter event; otherwise aliases collapse to the same raw event and lose their memory-location meaning.

## State And Persistence
The static state is the offcore request/response matrix. The important persisted values are the `MSRValue` bitmasks, which distinguish local DRAM, remote DRAM, all DRAM, and LLC-miss categories. There is no mutable state in the JSON itself.

## Dependencies And Integration Points
This table depends on Nehalem EX offcore response MSR semantics and perf support for `MSRIndex`/`MSRValue`. It integrates with `cache.json`, which contains broader offcore cache/location aliases. It is relevant for NUMA and memory locality diagnosis because local-vs-remote DRAM distinctions are encoded directly in alias names and filters.

## Risks
The primary risk is offcore filter drift. Since all aliases share `EventCode`, `UMask`, and counter, incorrect `MSRValue` values are hard to detect by superficial generated-code checks. Missing locality variants could weaken performance diagnostics on multi-socket Nehalem EX systems. Counter 2 binding can also create scheduling conflicts with other counter-2-only events.

## Test Signals
Validate JSON syntax and generated `pmu-events.c`. Inspect generated entries for representative aliases from each response class: `ANY_LLC_MISS`, `LOCAL_DRAM`, and `REMOTE_DRAM`. Hardware smoke tests should use at least one local and one remote DRAM alias where the platform can expose different traffic.
