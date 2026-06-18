# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/virtual-memory.json

## Purpose
This file defines 14 Nehalem EX virtual-memory PMU aliases for TLB misses, page walks, ITLB flushes, large ITLB hits, and precise retired translation misses. It is byte-identical to the Nehalem EP virtual-memory table.

## Important APIs, Types, And Fields
The objects use `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `SampleAfterValue`, and optional `PEBS`. The families are `DTLB_LOAD_MISSES`, `DTLB_MISSES`, `ITLB_FLUSH`, `ITLB_MISSES`, `ITLB_MISS_RETIRED`, `LARGE_ITLB`, `MEM_LOAD_RETIRED.DTLB_MISS`, and `MEM_STORE_RETIRED.DTLB_MISS`. Precise aliases are `ITLB_MISS_RETIRED`, `MEM_LOAD_RETIRED.DTLB_MISS`, and `MEM_STORE_RETIRED.DTLB_MISS`.

## Control Flow
The file is declarative. `jevents.py` loads it during perf builds for the Nehalem EX model, writes generated PMU-event C data, and runtime perf resolves event aliases to PMU encodings. The processor and kernel PMU layer perform counting and optional precise sampling.

## State And Persistence
Only static event metadata is persisted. The file has no runtime state or persistence behavior beyond generated tables. Default sample periods are `2000000`.

## Dependencies And Integration Points
It depends on Nehalem EX TLB event encodings and perf's x86 PMU alias schema. It integrates with the generated event table and complements `memory.json` and `cache.json`: those files describe data-source locality and cache behavior, while this file isolates address-translation pressure.

## Risks
The table is small but diagnostic-sensitive. Misencoding a page-walk or second-level TLB hit event can lead to incorrect conclusions about memory pressure. The precise retired aliases must preserve `PEBS`. The EP/EX duplication should be maintained unless architecture documentation justifies divergence.

## Test Signals
Use JSON validation, `jevents.py` generation, generated-table tests, and `perf list` inspection. Include tests that exercise one non-precise walk event and one PEBS retired DTLB/ITLB event.
