<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/memory.json

## Purpose

`memory.json` defines 67 Haswell-X core PMU events related to transactional memory, memory ordering, load latency sampling, misaligned memory references, and offcore LLC miss response classification. These entries provide raw event aliases used directly by `perf record/stat` and indirectly by higher-level metrics in `hsx-metrics.json`.

The file is declarative PMU metadata. Its API surface is the perf event JSON schema: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and optional `MSRIndex`, `MSRValue`, `PEBS`, `Data_LA`, `Errata`, `BriefDescription`, and `PublicDescription`.

## Important event families

Transactional memory events cover HLE and RTM lifecycle and abort categories: `HLE_RETIRED.START`, `HLE_RETIRED.COMMIT`, `HLE_RETIRED.ABORTED`, `HLE_RETIRED.ABORTED_MISC1` through `MISC5`, and the analogous `RTM_RETIRED.*` set. `TX_EXEC.MISC1` through `MISC5` and `TX_MEM.*` record transactional abort causes such as capacity write, conflict, HLE elision buffer mismatch/not-empty/unsupported-alignment, store to elided lock, and full elision buffer.

Load latency sampling is represented by `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_4`, `_8`, `_16`, `_32`, `_64`, `_128`, `_256`, and `_512`. These entries use counter 3, `Data_LA: 1`, PEBS level `2`, `MSRIndex: 0x3F6`, and different `MSRValue` thresholds. They are intended for precise latency sampling rather than ordinary aggregate counting.

Offcore response events use event codes `0xB7, 0xBB` with `MSRIndex: 0x1a6,0x1a7` and request/response filter `MSRValue` masks. The file defines aliases for code reads, data reads, all reads, all requests, RFOs, demand reads/RFOs, and L2/LLC prefetches, subdivided by LLC miss response classes such as `ANY_RESPONSE`, `LOCAL_DRAM`, `REMOTE_DRAM`, `REMOTE_HITM`, and `REMOTE_HIT_FORWARD`.

Other memory events include `MACHINE_CLEARS.MEMORY_ORDERING` and `MISALIGN_MEM_REF.LOADS`/`STORES`.

## Control flow and evaluation model

There is no file-local execution flow. Perf maps each `EventName` to an event selector made from `EventCode`, `UMask`, counter constraints, optional PEBS and data-address sampling flags, and optional model-specific register programming. When a user asks for an offcore event, perf must program the core event select plus the appropriate offcore response MSR filter.

The load-latency threshold events share the same core event encoding and differ mostly by latency threshold MSR value. The offcore aliases share the same PMU event codes and differ by filter masks. This makes the schema compact but means the correctness of `MSRValue` is central to the event semantics.

## State and persistence behavior

The JSON stores static event definitions only. Runtime state is the PMU programming performed by perf and the kernel: general-purpose counter allocation, PEBS buffer setup, data linear address capture, and MSR filter programming. `SampleAfterValue` values provide default sampling periods and affect profile granularity when used by perf.

## Dependencies and integration points

The file integrates with perf's PMU event generator, x86 core PMU event parser, PEBS support, offcore response MSR support, and metric formulas in `hsx-metrics.json`. Metrics for memory latency, DRAM/local/remote memory, data sharing, false sharing, and NUMA locality rely on these aliases or related offcore definitions.

The file also depends on Haswell-X errata handling and kernel support. Entries mark errata such as `HSD65`, `HSD76`, `HSD25`, and `HSM26`; users and tests need to interpret affected measurements carefully.

## Risks and maintenance notes

Offcore events are high risk because event code, umask, MSR index, and MSR filter masks must agree. A wrong `MSRValue` can silently count the wrong request or response class. Events using two possible offcore MSRs (`0x1a6,0x1a7`) may also interact with grouping and counter allocation limits.

PEBS/data-address events are sensitive to hardware support and kernel implementation. The latency events require counter 3 and precise sampling setup, so they can fail or be silently unavailable on mismatched systems. Transactional memory events may be unavailable or misleading on systems where TSX/HLE/RTM are disabled by microcode, BIOS policy, or security mitigations.

## Test signals

Validation should include JSON parsing, perf event table generation, `perf list` visibility for representative `HLE_RETIRED`, `RTM_RETIRED`, `TX_MEM`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, and `OFFCORE_RESPONSE.*` aliases, and hardware smoke tests for offcore MSR programming. Good command-level checks include `perf stat -e OFFCORE_RESPONSE.ALL_DATA_RD.LLC_MISS.LOCAL_DRAM` and PEBS sampling checks such as `perf record -e MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128` on Haswell-X hardware where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/memory.json -->
