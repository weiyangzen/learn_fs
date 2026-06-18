<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/cache.json

## Purpose
This JSON file defines Granite Rapids core cache, memory-retirement, offcore, and prefetch PMU events for perf. The complete 1,230-line file was read, containing 121 event records. It exposes L1D/L2 cache behavior, retired memory instructions, L3 hit/miss locality, offcore response classes including CXL memory, outstanding request cycles, and software prefetch access classes.

## Important APIs, Types, and Functions
The file uses core perf event fields including `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, optional `CounterMask`, and optional `EdgeDetect`. It has no `Unit`, so these are core PMU aliases. Event families include `OCR` (35), `L2_RQSTS` (18), `MEM_INST_RETIRED` (10), `OFFCORE_REQUESTS_OUTSTANDING` (8), `MEM_LOAD_RETIRED` (8), `OFFCORE_REQUESTS` (6), `SW_PREFETCH_ACCESS` (5), `MEM_LOAD_L3_MISS_RETIRED` (5), L1D pending-miss events (5), and smaller L1D/L2/LLC/SQ groups. OCR records use `EventCode` `0x2A,0x2B`, which `jevents.py` parses by taking the first code for sorting while preserving the string in generated event data.

## Control Flow, State, and Persistence
There is no executable control flow. The perf build pipeline reads the JSON, and `jevents.py` emits generated event descriptors. `SampleAfterValue` becomes `period=`, `UMask` becomes `umask=`, `CounterMask` becomes `cmask=`, and `EdgeDetect` becomes `edge=`. Runtime perf users consume aliases such as `l2_rqsts.*`, `mem_load_retired.*`, and `ocr.*`; counter values are collected by the kernel core PMU. The JSON is immutable source data, while `pmu-events.c` is the generated persistent artifact.

## Dependencies and Integration Points
The file depends on Granite Rapids x86 model mapping, perf's core PMU JSON schema, and kernel PMU support for the corresponding event encodings. It integrates with memory hierarchy analysis, CXL memory attribution, NUMA/SNC locality analysis, and offcore response diagnostics. It also pairs with Granite Rapids `counter.json`, which declares that the `core` unit has 4 fixed and 8 generic counters, constraining simultaneous measurement capacity.

## Risks and Test Signals
The file is dense and has several high-risk encoding patterns. All 121 records specify `SampleAfterValue`, six use `CounterMask`, one uses `EdgeDetect`, and OCR records include two event-select codes in one field. `jevents.py` explicitly splits `EventCode` on the first comma for sorting, so multi-code offcore definitions should be checked in generated output. CXL and remote-memory labels are user-visible and easy to misinterpret if masks are wrong. Test signals include `jq` validation, `jevents.py` generation without parsing errors, generated event strings retaining expected OCR/offcore configuration, `perf list` visibility, and hardware tests using cache-fitting, DRAM-streaming, remote-memory, and CXL-memory workloads when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/cache.json -->
