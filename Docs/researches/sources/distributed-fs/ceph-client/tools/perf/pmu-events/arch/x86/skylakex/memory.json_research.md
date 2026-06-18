# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/memory.json

## Purpose

`memory.json` is the Skylake Server PMU manifest for memory, offcore, transaction, and memory-ordering events. It defines 115 aliases. The file covers L3-miss stall cycles, HLE/RTM transactional outcomes, machine clears from memory ordering, precise load-latency thresholds, offcore request and response classifications, and TSX memory abort details.

As with the other PMU manifests, this file is build-time data for `jevents.py`. Its topic is derived from the filename as `memory`, and its events become generated perf aliases for the SkylakeX CPU table.

## Important Schema, APIs, and Event Families

The core schema fields are `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, descriptions, and optional special fields:

- `PEBS` marks precise-capable events. The load-latency aliases use `PEBS: "2"` and `Data_LA: "1"`, which causes `jevents.py` to append precise/address-support notes to descriptions.
- `MSRIndex` and `MSRValue` are central here. `0x3F6` maps to `ldlat=` for load-latency thresholds. `0x1A6` and `0x1A7` map to `offcore_rsp=` for offcore response filters.
- `Errata` is present for `MACHINE_CLEARS.MEMORY_ORDERING` with `SKL089`; `jevents.py` appends a spec-update note to descriptions.

Important event groups:

- `CYCLE_ACTIVITY.CYCLES_L3_MISS` and `CYCLE_ACTIVITY.STALLS_L3_MISS` on event `0xA3`, distinguishing outstanding L3 miss cycles from exposed execution stalls.
- `HLE_RETIRED.*` and `RTM_RETIRED.*` on events `0xC8` and `0xC9`, tracking transaction starts, commits, and abort classes.
- `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_{4,8,16,32,64,128,256,512}`, all using event `0xCD`, PEBS, data linear address support, MSR `0x3F6`, and threshold-specific `MSRValue`.
- `OFFCORE_REQUESTS*`, for demand data read L3 misses and outstanding request occupancy.
- `OFFCORE_RESPONSE.*`, a large matrix of request types and L3-miss response classes sharing `EventCode` `0xB7, 0xBB`, MSR selectors `0x1a6,0x1a7`, and distinct `MSRValue` filters.
- `TX_EXEC.*` and `TX_MEM.*`, for TSX execution and memory abort causes.

## Control Flow and Integration

`jevents.py` loads each object as a `JsonEvent`. For offcore response objects, it takes the first event code from the comma-separated `EventCode` field when constructing the base `event=` string, while the `MSRIndex`/`MSRValue` pair supplies the offcore response filter. The generated alias therefore depends on both the event selector and the model-specific offcore MSR bits.

At build time, this file contributes entries to the SkylakeX model event table. At runtime, perf exposes these names as event aliases for matching CPUs. The offcore and load-latency events rely on kernel support for programming the relevant MSRs and precise sampling modes.

## State and Persistence Behavior

The JSON file stores static event definitions only. The persistent output is generated C data in perf. Runtime state includes programmed PMU counters, PEBS records, offcore response MSR state, and sampled data addresses, all managed by perf and the kernel.

`SampleAfterValue` choices vary significantly. Load-latency thresholds use smaller periods for rarer events, for example `101` for `LOAD_LATENCY_GT_512` and `1009` for `LOAD_LATENCY_GT_128`, while broad events generally use larger periods. Those defaults affect sampling density and overhead.

## Dependencies

Dependencies include:

- Intel Skylake Server event encodings and offcore response filter bit layouts.
- `jevents.py` MSR mappings for `0x3F6`, `0x1A6`, and `0x1A7`.
- Kernel PMU support for PEBS, data address capture, TSX/HLE/RTM events, and offcore response MSRs.
- Perf alias generation and CPU model dispatch through the x86 mapfile.

## Risks and Edge Cases

The offcore response matrix is the most fragile part of the file. Many aliases share identical `EventCode`, `UMask`, `Counter`, and MSR index fields, with only `MSRValue` differentiating demand reads, RFOs, prefetches, local DRAM, remote DRAM, remote HITM, and snoop outcomes. A single bit error can silently redirect an alias to a different memory-source category.

Comma-separated `EventCode` and `MSRIndex` values rely on `jevents.py` behavior that uses the first value for conversion while preserving the intended offcore filter path. Any parser change must be checked against this pattern.

PEBS load-latency aliases report latency from dispatch to completion, not pure memory latency, according to the descriptions. Documentation and metric consumers should avoid treating these as direct DRAM-only latency counters.

TSX/HLE events may be unavailable, disabled, or affected by microcode and platform policy even when the alias exists. Perf alias availability does not guarantee a useful nonzero count on every SkylakeX deployment.

## Test Signals

Useful checks are:

- `jq empty memory.json` and a generated perf build to catch syntax and schema conversion failures.
- Inspection of generated event strings for `ldlat=` and `offcore_rsp=` fields.
- `perf list memory` and `perf list | grep -i offcore_response` on SkylakeX-class hardware.
- Targeted `perf stat` runs using `mem_trans_retired.load_latency_gt_64` and a representative `offcore_response.*` alias.
- Hardware-aware comparison of local/remote DRAM and HITM counters under NUMA or sharing workloads.
