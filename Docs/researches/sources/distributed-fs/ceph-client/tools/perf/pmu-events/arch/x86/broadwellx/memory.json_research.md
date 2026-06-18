# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/memory.json

## Purpose

`memory.json` defines 58 BroadwellX memory and transactional-memory events. It covers HLE/RTM retired transaction states, transaction abort reasons, transactional memory execution/memory diagnostics, misaligned memory references, memory-ordering machine clears, PEBS load-latency thresholds, and LLC-miss offcore response categories.

## Important APIs, types, and schema

The standard event schema appears with `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, `PEBS`, `Data_LA`, `Errata`, `MSRIndex`, and `MSRValue`. `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` entries use `MSRIndex` `0x3F6`, which `jevents.py` maps to `ldlat=...`, with `PEBS` value `2` and `Data_LA` indicating address support when precise. `OFFCORE_RESPONSE.*.LLC_MISS.*` entries use offcore response MSRs `0x1a6,0x1a7` and BroadwellX-specific response masks.

Important families are `HLE_RETIRED.*`, `RTM_RETIRED.*`, `TX_EXEC.*`, `TX_MEM.*`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_{4,8,16,32,64,128,256,512}`, `MISALIGN_MEM_REF.*`, `MACHINE_CLEARS.MEMORY_ORDERING`, and many `OFFCORE_RESPONSE.*.LLC_MISS.*` aliases for local DRAM, remote DRAM, remote HITM, remote hit-forward, demand RFO, all reads, all data reads, and code reads.

## Control flow and integration

The build assigns the topic `memory` and emits these as BroadwellX core events. `bdx-metrics.json` consumes the PEBS load-latency and offcore LLC-miss aliases in memory latency, NUMA, remote cache, remote memory, local memory, false-sharing, and store/lock latency formulas. Transactional-memory aliases are also used by generated Intel extra metrics in `intel_metrics.py` when TSX events are present.

## State and persistence behavior

The JSON is static; the generated perf binary stores the aliases. Runtime behavior is more stateful than simple events because PEBS load-latency entries program a latency MSR and require precise sampling support, while offcore events program offcore response MSRs. TSX/HLE events only produce meaningful counts on hardware and kernels where the transactional features are enabled and not disabled by microcode or policy.

## Dependencies

Dependencies include BroadwellX TSX/HLE PMU support, PEBS/Data Linear Address support, offcore response MSR support in `jevents.py`, and adjacent metric definitions. Several events carry errata labels such as `BDM100`, `BDM35`, and `BDE70`, so correct interpretation depends on Intel specification updates.

## Risks

The highest risk is semantic drift in offcore and latency MSR encodings: masks can be syntactically valid but count a different response class. PEBS latency events are constrained to counter 2 and precise sampling; using them in grouped metrics can fail or multiplex poorly if constraints are ignored. TSX events may be unavailable or misleading on systems where TSX is disabled. Errata-marked load-latency and offcore events need guarded interpretation in performance investigations.

## Test signals

Tests should validate JSON syntax, generated aliases for representative `mem_trans_retired.load_latency_gt_64`, `offcore_response.all_data_rd.llc_miss.local_dram`, `rtm_retired.aborted`, and `tx_mem.abort_conflict`, plus metric expansion for memory latency and NUMA metrics. Hardware smoke tests should verify PEBS load-latency events can be scheduled precisely and that offcore miss categories produce nonzero counts under memory-streaming workloads.
