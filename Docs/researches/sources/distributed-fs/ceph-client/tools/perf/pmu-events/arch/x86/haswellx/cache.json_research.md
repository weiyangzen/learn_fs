# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/cache.json

## Purpose

This file defines 97 HaswellX core cache, memory-request, and offcore events. HaswellX is selected for `GenuineIntel-6-3F`, and this file supplies server-oriented cache behavior aliases for L1D/L2/LLC behavior, fill-buffer pressure, outstanding offcore requests, retired memory uops, snoop outcomes, remote/local DRAM classifications, split locks, and store queue pressure.

## Important APIs, Types, And Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and sometimes `PublicDescription`. There is no `Unit`, so entries belong to the HaswellX core PMU.

Major families include `L1D.REPLACEMENT`, five `L1D_PEND_MISS` events, `L2_LINES_IN/OUT`, 16 `L2_RQSTS`, 8 `L2_TRANS`, `LONGEST_LAT_CACHE`, `MEM_LOAD_UOPS_RETIRED`, `MEM_LOAD_UOPS_L3_HIT_RETIRED`, `MEM_LOAD_UOPS_L3_MISS_RETIRED`, `MEM_UOPS_RETIRED`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `OFFCORE_REQUESTS_BUFFER.SQ_FULL`, 21 `OFFCORE_RESPONSE` aliases for LLC hit/snoop outcomes, `LOCK_CYCLES.CACHE_LOCK_DURATION`, and `SQ_MISC.SPLIT_LOCK`.

## Control Flow

`jevents.py` emits these records into the HaswellX model table based on the x86 mapfile. Runtime perf resolves aliases for direct use and for metrics that may be shared or generated for server Haswell variants. Offcore response aliases require the generator and runtime perf code to preserve the request/response encoding accurately.

## State And Persistence Behavior

The file stores static event metadata and sample periods. Cache line states, miss queues, fill buffers, snoop responses, and offcore request occupancy are measured by hardware during a run. No local state is persisted outside the generated perf tables.

## Dependencies And Integration Points

Integration points include HaswellX model matching, perf core PMU alias lookup, offcore response MSR handling, cache/memory performance workflows, and any metrics that use the names defined here. These aliases are especially relevant to server memory locality, snoop traffic, NUMA effects, and cache-sharing analysis.

## Risks And Edge Cases

Haswell and HaswellX share many names but not all event semantics; copying formulas or expectations between directories can be wrong. Offcore responses are dense encodings where request type, LLC hit/miss, snoop, local/remote, and prefetch distinctions must remain intact. Outstanding request events count occupancy or cycles with occupancy, not just request totals. Remote DRAM and HITM events require NUMA/cross-core conditions to be meaningful.

## Test Signals

Run `jq empty`, x86 `jevents.py` generation, `perf test pmu-events`, and representative `perf list` checks for `L2_RQSTS.*`, `MEM_LOAD_UOPS_RETIRED.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, and `OFFCORE_RESPONSE.*`. Runtime validation should use cache-fit versus cache-miss workloads, NUMA-local/remote memory placement, cross-core sharing, and store/write pressure.
