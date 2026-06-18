<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-cache.json

## Purpose
This JSON file defines Knights Landing uncore cache, home-agent, TOR, ring, credit, and ingress/egress queue PMU events for perf. It is declarative input to the perf PMU event generator, not executable code. The full 3,786-line array was read and contains 421 event records, all with `Unit` `CHA` and `PerPkg` `1`.

## Important APIs, Types, and Functions
The public API is the set of perf event aliases exported from each `EventName`. Records use the perf PMU JSON schema fields `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `PerPkg`, and `BriefDescription`; 420 records specify `EventCode`, 417 specify `UMask`, and the clock-like entries rely on the default generated `event=0` form plus unit metadata.

There are no functions or classes. The important event families include `UNC_H_TOR_OCCUPANCY` (12 records), `UNC_C_TOR_INSERTS` (7), `UNC_H_TOR_INSERTS` (6), many eight-way agent and ingress retry families such as `UNC_H_AG0_AD_CRD_ACQUIRED`, `UNC_H_AG1_BL_CRD_OCCUPANCY`, `UNC_H_INGRESS_RETRY_IPQ0_REJECT`, and `UNC_H_INGRESS_RETRY_REQ_Q0_RETRY`, plus horizontal and vertical egress/ring families. The file exposes a much larger Knights Landing CHA/home-agent taxonomy than the smaller KNL memory and I/O event files, covering TOR inserts/occupancy, cache line victimization, SF lookups, CMS agent credits, ring backpressure, nack/bypass/starvation signals, and ingress retry behavior.

## Control Flow
Control flow is external to this file. `tools/perf/pmu-events/Build` discovers JSON files under `pmu-events/arch` for the selected `JEVENTS_ARCH` and feeds them to `jevents.py`. `jevents.py` converts `Unit` `CHA` to Linux PMU name `uncore_cha`, converts `EventCode` to `event=`, `UMask` to `umask=`, and preserves non-zero event modifiers in generated event strings. The x86 map entry `GenuineIntel-6-(57|85),v16,knightslanding,core` selects this model's events at runtime. Perf then exposes aliases such as `unc_h_tor_occupancy.*` and `unc_h_ingress_retry_*` through `perf list` and resolves them for `perf stat -e` or related commands on Knights Landing hardware.

## State and Persistence
The source JSON has no mutable state. Its persistent effect is the generated `pmu-events.c` table compiled into perf. `PerPkg` is retained as per-package aggregation metadata, while the unit mapping controls which kernel PMU namespace receives the alias. Because all records are uncore per-package events, runtime interpretation also depends on the kernel uncore CHA PMU topology and the number of package instances visible on the host.

## Dependencies and Integration Points
This file depends on the perf PMU event JSON schema, `jevents.py`, `pmu-events.h`, the x86 CPU map in `arch/x86/mapfile.csv`, and the kernel uncore PMU driver exposing `uncore_cha`. It integrates with adjacent Knights Landing topics: `uncore-memory.json` for MCDRAM/iMC counters, `uncore-io.json` for M2PCIe ingress/egress activity, and `virtual-memory.json` for core page-walk signals. The event family naming also integrates with perf user workflows that compare broad TOR/cache/ring totals against narrower queue, direction, or agent-specific subsets.

## Risks
The highest risk is data correctness. Many families are repeated matrices over agents, transgress indices, queue IDs, horizontal/vertical directions, and AD/AK/BL/IV message classes; a copy/paste error in `UMask` or event suffix would silently expose a misleading counter. Heavy reuse of nearby event codes and masks makes review by visual inspection weak. The file has no `PublicDescription`, so perf users rely on terse `BriefDescription` strings that contain some duplicated spacing and vendor terminology. The four records without `UMask` and one record without `EventCode` are likely clock or aggregate-style entries, but generator behavior for missing fields should be checked whenever schema handling changes.

## Test Signals
Useful validation starts with `jq empty` over the file and a perf tools build that regenerates `pmu-events.c`. Generated aliases should contain `pmu=uncore_cha`, `perpkg=1`, expected `event=`/`umask=` terms, and no malformed default entries for missing masks. Hardware smoke tests should run broad TOR and ring events together with narrower subevents to check that aggregate directions, queue classes, and agent-specific counts move under cache-heavy, remote-memory, and ring-pressure workloads. Regression tests should especially diff generated event strings for repeated families such as `UNC_H_INGRESS_RETRY_*`, `UNC_H_AG*_CRD_*`, and `UNC_H_EGRESS_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-io.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-io.json

## Purpose
This JSON file defines Knights Landing M2PCIe uncore I/O PMU events for perf. It is static event metadata for measuring traffic between the M2PCIe block and CMS, including ingress queue occupancy and egress queue inserts, fullness, and non-empty cycles. The complete 218-line array was read and contains 24 records, all with `Unit` `M2PCIe` and `PerPkg` `1`.

## Important APIs, Types, and Functions
The exported API is the perf alias set under event families `UNC_M2P_EGRESS_INSERTS` (8 records), `UNC_M2P_EGRESS_CYCLES_FULL` (6), `UNC_M2P_EGRESS_CYCLES_NE` (6), and `UNC_M2P_INGRESS_CYCLES_NE` (4). The schema fields are consistently `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, `UMask`, and `Unit`. Counters are mostly `0,1,2,3`, with `UNC_M2P_EGRESS_CYCLES_NE.*` limited to `0,1`.

There are no local functions or types beyond the JSON record shape. The suffixes model message classes and lanes: `AD_0`, `AD_1`, `AK_0`, `AK_1`, `BL_0`, `BL_1`, plus `AK_CRD_0` and `AK_CRD_1` for egress inserts, and ingress selectors such as `ALL`, `CBO_IDI`, `CBO_NCB`, and `CBO_NCS`.

## Control Flow
The perf build includes this file through the generic `SRC_JSON` discovery in `tools/perf/pmu-events/Build`. `jevents.py` maps `Unit` `M2PCIe` to PMU name `uncore_m2pcie`, emits `EventCode` as `event=`, emits non-zero `UMask` as `umask=`, and preserves `PerPkg`. Runtime selection comes from the Knights Landing x86 map row `GenuineIntel-6-(57|85),v16,knightslanding,core`, after which perf exposes the generated M2PCIe aliases for uncore counting.

## State and Persistence
The file has no mutable runtime state. Persistent behavior is the generated perf event table. All records are per-package uncore aliases, so actual counter availability and instance enumeration are provided by the kernel `uncore_m2pcie` PMU. The descriptions encode the intended state being sampled: egress full cycles, egress non-empty cycles, egress queue inserts, and ingress non-empty cycles.

## Dependencies and Integration Points
Dependencies are the perf PMU JSON schema, `jevents.py`, the x86 model map, and the kernel uncore driver for Knights Landing M2PCIe. It integrates with the larger Knights Landing uncore picture by complementing `uncore-cache.json` ring/CMS traffic and `uncore-memory.json` memory-controller counters. Workloads involving PCIe devices, DMA, or I/O-originated memory traffic can correlate these aliases with cache home-agent and memory events to locate backpressure between M2PCIe and CMS.

## Risks
The file is small but matrix-like, so the main risk is mismatched lane suffixes and `UMask` values. The `UNC_M2P_EGRESS_INSERTS` masks include both base traffic classes and credit classes, while the cycles-full and cycles-not-empty families omit credit selectors; users can accidentally compare non-equivalent sets. The `BriefDescription` text contains duplicated words and terse class names, so generated `perf list` help is not self-explanatory. Counter constraints differ between families, and scheduler behavior can fail if users combine too many events with the `0,1`-limited egress non-empty records.

## Test Signals
Validation should include `jq empty`, successful `jevents.py` generation, and generated event strings under `uncore_m2pcie` with `perpkg=1` and the expected `event=0x10`, `0x23`, `0x24`, and `0x25` codes. Hardware tests should compare `UNC_M2P_INGRESS_CYCLES_NE.ALL` against the CBO-specific selectors and exercise PCIe/DMA traffic to ensure egress insert and fullness counters move. Multiplexing tests should verify the limited-counter `UNC_M2P_EGRESS_CYCLES_NE.*` records are schedulable only within their declared counter constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-io.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-memory.json

## Purpose
This JSON file defines Knights Landing uncore memory-controller PMU events for perf. It covers MCDRAM EDC access, EDC read/write queue inserts, EDC clockticks, DDR iMC CAS counts, and iMC clockticks. The complete 120-line array was read and contains 14 records across `EDC_ECLK`, `EDC_UCLK`, `iMC_DCLK`, and `iMC_UCLK` units, all with `PerPkg` `1`.

## Important APIs, Types, and Functions
There are no functions or classes; the file's API is its perf aliases. Event families are `UNC_E_EDC_ACCESS` (5 records), `UNC_M_CAS_COUNT` (3), `UNC_E_RPQ_INSERTS`, `UNC_E_WPQ_INSERTS`, `UNC_E_E_CLOCKTICKS`, `UNC_E_U_CLOCKTICKS`, `UNC_M_D_CLOCKTICKS`, and `UNC_M_U_CLOCKTICKS`. Ten records have explicit `EventCode` and `UMask`; the four clocktick records omit one or both of those fields and rely on generator defaults plus their `Unit`.

The `UNC_E_EDC_ACCESS.*` records distinguish MCDRAM cache hits and misses by clean, dirty, and invalid state. `UNC_E_RPQ_INSERTS` and `UNC_E_WPQ_INSERTS` count MCDRAM read and write requests across flat, cache, and hybrid memory modes. `UNC_M_CAS_COUNT.RD`, `.WR`, and `.ALL` expose DDR CAS traffic through the iMC DCLK domain.

## Control Flow
The file is discovered by `tools/perf/pmu-events/Build` and parsed by `jevents.py`. Units not explicitly listed in the fixed unit table are converted to lowercase uncore PMU names, so `EDC_ECLK` becomes `uncore_edc_eclk`, `EDC_UCLK` becomes `uncore_edc_uclk`, `iMC_DCLK` becomes `uncore_imc_dclk`, and `iMC_UCLK` becomes `uncore_imc_uclk`. `EventCode` and `UMask` become generated `event=` and `umask=` fields when present, and zero/missing values are omitted or defaulted according to generator behavior. The Knights Landing model map row selects these aliases for family/model `GenuineIntel-6-(57|85)`.

## State and Persistence
The JSON is immutable source metadata. Persistence is the generated perf event table, and runtime state lives only in hardware PMU counters and kernel uncore PMU instances. The file's descriptions contain important mode semantics: several EDC access events are valid only in MCDRAM cache or hybrid mode, while RPQ/WPQ inserts are valid in flat, cache, and hybrid modes.

## Dependencies and Integration Points
Dependencies include the perf JSON schema, `jevents.py`, x86 model mapping, and kernel uncore drivers for the EDC and iMC clock domains. The file integrates with Knights Landing memory-mode analysis: MCDRAM hit/miss cleanliness comes from EDC events, DDR bandwidth comes from iMC CAS counts, and clockticks provide normalization denominators. It pairs naturally with `uncore-cache.json` TOR/home-agent traffic and `uncore-io.json` M2PCIe traffic when attributing memory pressure.

## Risks
Mode validity is the main semantic risk. EDC cache hit/miss events are not meaningful in every MCDRAM configuration, so users can misread flat-mode counts without checking platform mode. Unit naming is another risk because `jevents.py` derives uncore PMU names from mixed-case strings; kernel PMU naming must match the derived lowercase names. Missing `EventCode`/`UMask` on clockticks is intentional-looking but should be guarded by generated-output tests. `UNC_E_EDC_ACCESS.MISS_INVALID` has a terse description compared with the other MCDRAM events, increasing user-facing ambiguity.

## Test Signals
Test with `jq empty`, a perf tools build, and generated aliases under the expected `uncore_edc_*` and `uncore_imc_*` PMUs. Hardware smoke tests should run in flat, cache, and hybrid MCDRAM modes where available, checking that EDC access events behave according to their stated mode validity. Bandwidth validation can compare `UNC_M_CAS_COUNT.RD/WR/ALL` ratios and use clockticks to normalize rates. Generated C diffs should flag any accidental loss of `PerPkg` or unit-derived PMU names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/virtual-memory.json

## Purpose
This JSON file defines Knights Landing core virtual-memory PMU events for perf. It exposes DTLB miss retirement and page-walk cycle/walk counters. The complete 65-line array was read and contains 7 records: one `MEM_UOPS_RETIRED` DTLB-miss load event and six `PAGE_WALKS` events.

## Important APIs, Types, and Functions
The records use core PMU schema fields `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`, with optional `PublicDescription`, `PEBS`, `Data_LA`, and `EdgeDetect`. There is no `Unit`, so `jevents.py` maps the records to `default_core` rather than an uncore PMU.

`MEM_UOPS_RETIRED.DTLB_MISS_LOADS` is precise (`PEBS` `1`) and supports address reporting through `Data_LA`. The `PAGE_WALKS.*_CYCLES` records count cycles with D-side, I-side, or any page walk in progress. The `PAGE_WALKS.*_WALKS` records use `EdgeDetect` to count completed or started walks rather than occupancy cycles, with sample periods of `100003` instead of the `200003` used by cycle-style events.

## Control Flow
The perf build discovers this JSON through `tools/perf/pmu-events/Build`. `jevents.py` maps missing `Unit` to `default_core`, converts `EventCode` to `event=`, `UMask` to `umask=`, `SampleAfterValue` to `period=`, `EdgeDetect` to `edge=`, and appends description text for precise/address-capable events. The x86 map row `GenuineIntel-6-(57|85),v16,knightslanding,core` selects these aliases for Knights Landing systems.

## State and Persistence
The file has no mutable state. Generated perf tables persist the alias names, event encodings, sampling periods, PEBS support, and edge-detect modifiers. Runtime behavior depends on core PMU support for PEBS and data linear address capture for the retired DTLB miss load event.

## Dependencies and Integration Points
Dependencies are perf's PMU JSON schema, `jevents.py`, x86 CPU model mapping, and core PMU support for the documented event encodings. The file integrates with `perf stat` and `perf record` for TLB and page-walk analysis. It is especially useful alongside Knights Landing memory and cache events when diagnosing whether memory latency originates from translation walks rather than MCDRAM/DDR/cache traffic.

## Risks
The main risk is confusing cycle occupancy events with edge-detected walk-count events. Several records share `EventCode` `0x05` and differ only by `UMask` and `EdgeDetect`, so a bad mask or dropped `edge=1` changes semantics completely. The DTLB miss event depends on precise sampling and data address support; losing `PEBS` or `Data_LA` metadata would make sampling workflows less useful even if the raw event still counts. The file also has no `Unit`, so accidental insertion of an uncore unit would move aliases to the wrong PMU namespace.

## Test Signals
Validate JSON syntax and generated event strings containing `period=`, `umask=`, and `edge=1` for the walk-count records. `perf list` should show the aliases as core events, not uncore events. Hardware tests should compare D-side and I-side page-walk behavior under pointer-chasing, instruction-cache/TLB stress, 4K page workloads, and huge-page workloads. `perf record` tests for `MEM_UOPS_RETIRED.DTLB_MISS_LOADS` should verify precise sampling and address availability when the platform supports it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/cache.json

## Purpose
This JSON file defines Lunar Lake cache, memory-access, offcore-response, L2, LLC, load/store retirement, prefetch, lock, and memory-bound stall PMU events for perf. The complete 1,694-line array was read and contains 166 records: 88 `cpu_core` records and 78 `cpu_atom` records for Lunar Lake's hybrid core/atom PMU model.

## Important APIs, Types, and Functions
The file uses perf event schema fields including `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `SampleAfterValue`, `BriefDescription`, and frequent `PublicDescription`. Additional modifiers include `Data_LA` on 47 records, `MSRIndex`/`MSRValue` on 23 offcore-response or latency-threshold records, `CounterMask` on 5 records, and `Deprecated` on 2 records. There are no functions or classes; the exported API is the alias set generated from these records.

Major families include `MEM_UOPS_RETIRED` (21), `MEM_INST_RETIRED` (15), `OCR` offcore response events (15), `L2_RQSTS` (11), `MEM_LOAD_RETIRED` (9), `OFFCORE_REQUESTS_OUTSTANDING` (8), `L2_LINES_IN`/`L2_LINES_OUT`/`L2_REQUEST` (6 each), `SW_PREFETCH_ACCESS`, `OFFCORE_REQUESTS`, `MEM_LOAD_UOPS_RETIRED`, `MEM_BOUND_STALLS_LOAD`, `MEM_BOUND_STALLS_IFETCH`, and `LLC_PREFETCHES_THROTTLED` (5 each). Several event names intentionally appear twice with different `Unit` values, such as `OCR.DEMAND_DATA_RD.ANY_RESPONSE`, `L2_REQUEST.ALL`, and `LONGEST_LAT_CACHE.MISS`, so the unit is part of the public API.

## Control Flow
`tools/perf/pmu-events/Build` discovers this file and `jevents.py` parses it into generated perf tables. `jevents.py` maps `Unit` `cpu_core` and `cpu_atom` directly to those PMU names, turns `EventCode` into `event=`, `UMask` into `umask=`, `SampleAfterValue` into `period=`, `CounterMask` into `cmask=`, and `MSRIndex`/`MSRValue` into offcore or frontend MSR terms when supported by `lookup_msr`. The x86 map entry `GenuineIntel-6-BD,v1.21,lunarlake,core` selects this model's generated aliases. At runtime, perf resolves the same alias name separately for P-core and E-core PMUs when both units are present.

## State and Persistence
The JSON is static metadata. Persistent output is the generated `pmu-events.c` table with core/atom PMU names, periods, deprecation flags, offcore MSR encodings, and address-capable descriptions. Runtime state is limited to hardware counters, PMU scheduling, and offcore MSR programming performed by perf/kernel code. `Data_LA` marks address-capable precise-style memory events in generated descriptions, while `MSRIndex` and `MSRValue` are essential for offcore-response filtering and atom load-latency thresholds.

## Dependencies and Integration Points
Dependencies include the perf PMU JSON schema, `jevents.py`, `pmu-events.h`, x86 mapfile selection, hybrid PMU support for `cpu_core` and `cpu_atom`, and MSR filter support for offcore response registers `0x1a6/0x1a7` and latency threshold MSR `0x3F6`. The file integrates with top-down memory-bound analysis, cache hierarchy studies, prefetch tuning, offcore response attribution, and load/store retirement sampling. It is closely related to Lunar Lake virtual-memory, frontend, pipeline, and floating-point topics because memory stalls often need correlation with TLB walks, frontend fetch stalls, and vector workload intensity.

## Risks
Hybrid duplication is the largest risk: the same `EventName` can have different encodings, counters, descriptions, and units for `cpu_core` and `cpu_atom`, so tooling must not deduplicate by name alone. Offcore events depend on correct `MSRIndex`/`MSRValue` translation; wrong handling silently measures different response classes. `Data_LA` appears on many retired memory events, so dropping that field reduces sampling diagnostic value. Two deprecated records and several intentionally overlapping aggregate/detail aliases can lead to double counting or outdated usage if surfaced without deprecation metadata. Counter constraints differ sharply, including single-counter `L1D_PENDING.*` records and broader `0..9` P-core events.

## Test Signals
Validation should include `jq empty`, perf generation, and inspection of generated strings for `pmu=cpu_core` versus `pmu=cpu_atom`, `period=`, `cmask=`, and offcore MSR terms. `perf list` on Lunar Lake should show both unit-specific aliases where duplicates exist. Hardware smoke tests should cover P-core and E-core pinning separately, cache-hit/miss microbenchmarks, split/locked access tests, prefetch-heavy loops, and offcore DRAM/LLC response workloads. Regression tests should ensure deprecated flags remain attached and that duplicate alias names are preserved as unit-specific records rather than collapsed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/floating-point.json

## Purpose
This JSON file defines Lunar Lake floating-point, SIMD/vector integer, FP assist, FP divide, and FP retirement PMU events for perf. The complete 484-line array was read and contains 51 records: 29 `cpu_core` records and 22 `cpu_atom` records for the hybrid Lunar Lake PMU model.

## Important APIs, Types, and Functions
The file uses `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `SampleAfterValue`, and `BriefDescription`, with optional `PublicDescription`, `CounterMask`, and `Deprecated`. There are no functions or classes. Event families include `FP_ARITH_INST_RETIRED` (11), `FP_ARITH_OPS_RETIRED` (11), `FP_INST_RETIRED` (7), `FP_VINT_UOPS_EXECUTED` (7), `ARITH` (4), `FP_ARITH_DISPATCHED` (4), `FP_FLOPS_RETIRED` (3), `ASSISTS` (2), plus `MACHINE_CLEARS` and `UOPS_RETIRED`.

The P-core side exposes detailed FP arithmetic retirement aliases, deprecated compatibility aliases under `FP_ARITH_INST_RETIRED.*`, port dispatch aliases `FP_ARITH_DISPATCHED.V0` through `.V3`, and assist/machine-clear events. The atom side exposes `ARITH.FPDIV_*`, `FP_INST_RETIRED.*`, `FP_FLOPS_RETIRED.*`, and `FP_VINT_UOPS_EXECUTED.*` events. `ARITH.FPDIV_ACTIVE` exists for both `cpu_atom` and `cpu_core` with different encodings.

## Control Flow
The file is discovered by `tools/perf/pmu-events/Build` and parsed by `jevents.py`. `Unit` is mapped directly to `cpu_core` or `cpu_atom`; `EventCode` and `UMask` become generated config terms; `CounterMask` becomes `cmask=` for active-cycle style events; `SampleAfterValue` becomes `period=`, and `Deprecated` is preserved in the generated event metadata. The Lunar Lake map row `GenuineIntel-6-BD,v1.21,lunarlake,core` selects the generated aliases at runtime.

## State and Persistence
The JSON file has no mutable state. Its durable effect is the generated perf event table, including unit-specific alias definitions and deprecated flags. Runtime state is in hardware counters and perf scheduling. Because this is a hybrid CPU event file, users may see different FP visibility and event availability depending on whether a workload runs on P-cores or E-cores.

## Dependencies and Integration Points
Dependencies are perf's PMU event schema, `jevents.py`, x86 mapfile selection, and hybrid `cpu_core`/`cpu_atom` PMU support. The file integrates with HPC and numerical workload profiling, vector width/FLOP accounting, FP divide bottleneck analysis, SSE/AVX transition diagnostics, and assist detection. It should be read together with Lunar Lake cache and execution/topdown events when separating arithmetic throughput limits from memory stalls or frontend/backend pipeline pressure.

## Risks
The main risk is hybrid semantic mismatch. Some concepts exist on both units with different event codes and masks, while other families are unit-specific; scripts must filter by `Unit` rather than assuming one alias applies to all cores. Nine `FP_ARITH_INST_RETIRED.*` records are deprecated in favor of `FP_ARITH_OPS_RETIRED.*`, so user-facing tooling should surface deprecation and avoid recommending old aliases. Aggregate aliases such as scalar/vector or FLOPS groups overlap narrower width/type records, creating double-counting risk. Public descriptions are present on only 12 records, leaving many atom-side aliases terse.

## Test Signals
Validation should include JSON syntax checks and generated event inspection for `pmu=cpu_core`, `pmu=cpu_atom`, `period=`, `cmask=`, and `deprecated=1` where expected. `perf list` should expose both unit-specific `ARITH.FPDIV_ACTIVE` forms without collapsing them. Hardware smoke tests should pin FP-heavy workloads to P-cores and E-cores separately, exercising scalar FP, 128-bit and 256-bit vectors, FP divide/sqrt loops, SSE/AVX mix cases, vector integer operations, and FP assists. Regression checks should confirm deprecated aliases remain aliases while newer `FP_ARITH_OPS_RETIRED.*` names are available for preferred analysis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/floating-point.json -->
