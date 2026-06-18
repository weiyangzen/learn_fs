<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-cache.json

## Purpose
This JSON file defines the Grand Ridge x86 uncore cache and home-agent PMU event topic for perf. It is static data consumed by the perf PMU event generator, not executable code. The complete 2,117-line file was read, containing 207 event records: 205 `CHA` records and 2 `CHACMS` records.

## Important APIs, Types, and Functions
The file uses the perf PMU JSON schema with `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `PerPkg`, `BriefDescription`, optional `PublicDescription`, optional `PortMask`, and optional `Experimental`. There are no functions or classes; the important "API" is the set of aliases exported to perf users. Event families are `UNC_CHA_TOR_INSERTS` (80), `UNC_CHA_TOR_OCCUPANCY` (73), `UNC_CHA_LLC_LOOKUP` (20), `UNC_CHA_LLC_VICTIMS` (11), `UNC_CHA_REQUESTS` (6), `UNC_CHA_IMC_WRITES_COUNT` (4), `UNC_CHA_OSB` (4), `UNC_CHA_DISTRESS_ASSERTED` (3), plus clock, misc, and IRQ queue events. The two `CHACMS` records expose clockticks and ring source throttle events, both using `PortMask` `0x000`.

## Control Flow, State, and Persistence
Control flow is external. `tools/perf/pmu-events/Build` includes this JSON in the `SRC_JSON` set, then `jevents.py` parses each record into generated `pmu-events.c`. In `jevents.py`, `EventCode` becomes `event=...`, `UMask` becomes `umask=...`, `PortMask` becomes `ch_mask=...`, and `PerPkg` is preserved as per-package aggregation metadata. The generated C table is compiled into perf, and at runtime perf resolves aliases such as `unc_cha_tor_inserts.*` against matching Grand Ridge CPU map entries. The file itself has no mutable state; persistence is the source JSON plus the generated perf event table.

## Dependencies and Integration Points
This topic depends on the perf PMU event JSON schema, x86 Grand Ridge model mapping, `jevents.py`, `pmu-events.h`, and the kernel uncore PMU drivers that expose `uncore_cha` and `uncore_chacms` PMUs. It integrates with `perf list` discoverability, `perf stat -e <alias>`, per-package uncore counting, and generated table lookup. The event definitions are also logically related to adjacent Grand Ridge uncore topics: memory-controller writes in `uncore-memory.json`, interconnect routing in `uncore-interconnect.json`, and I/O-originated transactions in `uncore-io.json`.

## Risks and Test Signals
Risks are mainly data correctness risks: 65 records are marked `Experimental`, many TOR masks are wide multi-bit encodings, and a wrong `UMask` can silently count a different transaction class. `EventCode` `0x35` and `0x36` are reused heavily for TOR inserts and occupancy, so copy/paste errors in masks are high impact. Port-mask handling matters because `jevents.py` emits non-zero `PortMask` as `ch_mask`; zero values are omitted from the generated event string. Test signals include `jq` syntax validation, successful `jevents.py` generation, generated `pmu-events.c` diffs, `perf list` entries under the Grand Ridge model, and hardware smoke tests comparing broad aggregate events such as `UNC_CHA_TOR_INSERTS.ALL` against narrower IA/IO/local subsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-interconnect.json

## Purpose
This JSON file defines Grand Ridge uncore interconnect PMU events for perf. The complete 275-line file was read, containing 29 event records across the `B2CMI`, `IRP`, and `UBOX` units. Its purpose is to expose mesh-to-memory, interconnect request path, snoop response, and uncore message events as symbolic perf aliases.

## Important APIs, Types, and Functions
The file is declarative and uses perf event fields such as `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `PerPkg`, `BriefDescription`, `PublicDescription`, and `Experimental`. It defines 15 `B2CMI` events for clockticks, direct-to-core behavior, IMC reads/writes, prefcam inserts/occupancy, tracker inserts/occupancy, and write-tracker inserts. It defines 13 `IRP` events for interconnect clockticks, cache occupancy, FAF inserts/occupancy, fast request/reject, lost forward, snoop response classes, and write-prefetch transactions. One `UBOX` event, `UNC_U_EVENT_MSG.MSI_RCVD`, tracks MSI messages received by the uncore box. All records use uncore counter lists such as `0,1,2,3` or `0,1`.

## Control Flow, State, and Persistence
There is no in-file control flow. During the perf build, `jevents.py` reads this topic and maps each record into a generated event descriptor. `Unit` is converted to PMU names such as `uncore_b2cmi`, `uncore_irp`, and `uncore_ubox`; `EventCode` and non-zero `UMask` values become perf event config terms. `PerPkg` marks these records as package-level uncore events. Persistence is limited to the checked-in JSON and generated `pmu-events.c`; runtime counter values exist only in perf sessions.

## Dependencies and Integration Points
The file depends on Grand Ridge uncore PMU support in the kernel and on the perf PMU event generator accepting the Intel uncore schema. It integrates with Grand Ridge mapfile matching, `perf list`, and `perf stat` aliases for interconnect traffic analysis. It complements `uncore-cache.json` by describing traffic after CHA routing and complements `uncore-memory.json` by describing reads/writes moving toward the memory controller.

## Risks and Test Signals
Fourteen records are marked `Experimental`, so users and maintainers should treat the semantics as less stable. Only two records include `PublicDescription`, which reduces user-facing detail in `perf list`. The file uses several related B2CMI read/write masks (`0x101`, `0x104`, `0x108`, `0x110`), so validation should look for swapped normal/all/DDR-as-memory semantics. Test signals include JSON parsing, `jevents.py` generation, alias presence for `unc_b2cmi_*`, `unc_i_*`, and `unc_u_*`, and hardware checks that aggregate read/write events exceed or match narrower subevents under controlled memory traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-io.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-io.json

## Purpose
This JSON file defines Grand Ridge integrated I/O (`IIO`) uncore PMU events for perf. The complete 1,380-line file was read, containing 121 event records. It gives perf symbolic names for PCIe completion buffering, CPU-to-I/O and I/O-to-CPU data and transaction requests, IOMMU activity, target routing, and posted write tracker occupancy.

## Important APIs, Types, and Functions
The schema fields include `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `PerPkg`, `BriefDescription`, `PortMask`, and frequent `FCMask`. All records use `Unit` `IIO`; 108 records include `FCMask`, and many records include `PortMask` values for `ALL_PARTS` or individual partitions. Event families are `UNC_IIO_DATA_REQ_OF_CPU` (24), `UNC_IIO_TXN_REQ_OF_CPU` (24), `UNC_IIO_DATA_REQ_BY_CPU` (18), `UNC_IIO_TXN_REQ_BY_CPU` (16), completion-buffer inserts and occupancy (9 each), `UNC_IIO_NUM_REQ_OF_CPU_BY_TGT` (8), `UNC_IIO_IOMMU0` (7), `UNC_IIO_IOMMU1` (4), plus `UNC_IIO_CLOCKTICKS` and `UNC_IIO_PWT_OCCUPANCY`. Port masks range across partition selectors such as `0x001` through `0x080` and aggregate `0x0FF`.

## Control Flow, State, and Persistence
This is build-time input. `jevents.py` translates `EventCode` into `event=`, `UMask` into `umask=`, `PortMask` into `ch_mask=`, and `FCMask` into `fc_mask=`. Zero-valued masks are omitted by canonicalization, while non-zero masks constrain the generated perf alias. At runtime, perf only sees generated aliases bound to the Grand Ridge `uncore_iio` PMU. There is no mutable state in the file; persistent behavior is the resulting generated C table compiled into perf.

## Dependencies and Integration Points
The file depends on the IIO uncore PMU implementation in the kernel and on perf's JSON generator knowing `FCMask` and `PortMask`. It integrates with PCIe/IOMMU performance analysis, device traffic attribution by partition, and memory request tracing between CPU and I/O agents. It relates to `virtual-memory.json` through IOMMU page-walk signals and to cache/interconnect topics through peer writes and CPU memory read/write transactions.

## Risks and Test Signals
Sixty-one records are marked `Experimental`, and only one record has `PublicDescription`, so the table is rich but user-facing semantics are sparse. The highest risk area is the repeated partition expansion pattern: a wrong `PortMask` or missing `ALL_PARTS` counterpart can make per-part totals impossible to reconcile. `FCMask` is present on most traffic records and is emitted as `fc_mask=`, so generator regressions in field handling would affect almost the whole file. Test signals include syntax validation, generated event strings containing expected `fc_mask` and `ch_mask` terms, `perf list` visibility under `uncore_iio`, and hardware tests that compare `ALL_PARTS` events against the sum of `PART0` through `PART7` for PCIe completion and CPU request traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-io.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-memory.json

## Purpose
This JSON file defines Grand Ridge integrated memory controller (`IMC`) uncore PMU events for perf. The complete 789-line file was read, containing 80 event records. It exposes DRAM command counts, subchannel CAS counts, read/write queue inserts and occupancy, powerdown cycles, MR4/refresher activity, and throttle cycles.

## Important APIs, Types, and Functions
Records use the perf PMU JSON schema fields `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `PerPkg`, `BriefDescription`, optional `PublicDescription`, and optional `Experimental`. Every event uses `Unit` `IMC` and counters `0,1,2,3`. Event families include `UNC_M_CAS_COUNT_SCH0` and `UNC_M_CAS_COUNT_SCH1` (7 each), `UNC_M_POWERDOWN_CYCLES` (8), `UNC_M_RPQ_INSERTS` and `UNC_M_WPQ_INSERTS` (6 each), `UNC_M_ACT_COUNT` (4), `UNC_M_PRE_COUNT` (5), MR4 and PDC activity (4 each), bandwidth/power throttle records, and queue occupancy records with separate event codes for each subchannel/physical channel.

## Control Flow, State, and Persistence
The file has no executable control flow. During perf build, `jevents.py` converts these records into generated event descriptors for the `uncore_imc` PMU. `EventCode` and `UMask` define the raw event config; `PerPkg` identifies package-level uncore aggregation. At runtime, perf resolves symbolic aliases and the kernel reads memory-controller PMU counters. No state is written back to this JSON; generated `pmu-events.c` is the derived persistent artifact.

## Dependencies and Integration Points
The file depends on Grand Ridge IMC uncore PMU support and on the perf PMU event build pipeline. It integrates with memory bandwidth and latency diagnostics, DRAM page policy analysis, queue occupancy analysis, and power/throttle investigations. It is a downstream counterpart to cache and interconnect events: CHA and B2CMI events describe requests before the IMC, while this file describes command and queue activity at the controller.

## Risks and Test Signals
Forty-eight records are marked `Experimental`, and only 31 include `PublicDescription`. Risk centers on subchannel and slot/rank mask correctness: SCH0/SCH1 and PCH0/PCH1 variants use nearby masks, making transposition easy. Occupancy events use distinct event codes instead of masks, so generator output should be checked for both encoded styles. Test signals include `jq` validation, `jevents.py` generation, presence of `unc_m_*` aliases, consistency checks that all/read/write CAS and activate/precharge events behave monotonically under memory load, and sanity checks that throttle/powerdown counters remain low or zero on unconstrained systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-power.json

## Purpose
This JSON file defines the Grand Ridge uncore power-control topic for perf. The complete 11-line file was read, containing a single `PCU` event record, `UNC_P_CLOCKTICKS`. Its purpose is to expose the PCU clock as a wall-time-like uncore reference counter.

## Important APIs, Types, and Functions
The record uses `EventName`, `EventCode`, `Unit`, `Counter`, `PerPkg`, `BriefDescription`, and `PublicDescription`. `EventCode` is `0x01`, `Unit` is `PCU`, counters are `0,1,2,3`, and `PerPkg` is `1`. There are no functions or classes. The exported alias is the PMU event name that perf users can request when the Grand Ridge `uncore_pcu` PMU is present.

## Control Flow, State, and Persistence
`jevents.py` converts the single record into a generated event descriptor with `event=0x1` and PMU name derived from `PCU`. Because the record has no `UMask`, `PortMask`, or other filters, the generated event string is simple. Runtime perf reads the PCU counter through the kernel PMU driver. State is static; the JSON is source data and the generated C table is the build artifact.

## Dependencies and Integration Points
The file depends on perf's PMU event schema and on kernel support for the Grand Ridge PCU uncore PMU. It integrates with package-level timing for other uncore measurements, where PCU clockticks can be used as a reference for elapsed uncore time or power-management state analysis.

## Risks and Test Signals
The main risk is availability: if the platform or kernel does not expose the PCU PMU, the alias may be generated but unusable at runtime. Since this file has only one event, schema breakage is easy to detect. Test signals include JSON validation, generated `unc_p_clockticks` alias presence, `perf list` visibility, and a `perf stat` smoke test confirming the counter increments near the documented fixed 1 GHz PCU clock while enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/virtual-memory.json

## Purpose
This JSON file defines Grand Ridge core virtual-memory PMU events for perf. The complete 148-line file was read, containing 17 records. It exposes DTLB load misses, DTLB store misses, ITLB misses, and a load-head DTLB miss retirement signal.

## Important APIs, Types, and Functions
The records use core event fields `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and optional `PublicDescription`. Unlike the uncore files, these records have no `Unit`, so `jevents.py` treats them as core PMU events. Event families are `DTLB_LOAD_MISSES` (5), `DTLB_STORE_MISSES` (5), `ITLB_MISSES` (6), and `LD_HEAD` (1). All records specify counters `0,1,2,3,4,5,6,7` and include `SampleAfterValue`; load events use period-like values such as `200003`, while store and instruction walk events use larger defaults such as `2000003`.

## Control Flow, State, and Persistence
The file is declarative build input. `jevents.py` converts `EventCode` and `UMask` into core PMU config terms and maps `SampleAfterValue` to generated `period=` metadata. Perf then exposes aliases for TLB walk completion, page-size-specific walks, STLB hits, walk-pending cycles, and retirement-time DTLB-miss detection. The file has no mutable state; generated perf tables are the persistent derivative.

## Dependencies and Integration Points
It depends on perf's x86 core PMU event support and Grand Ridge model mapping. It integrates with `perf stat`, `perf record`, and event sampling defaults through `SampleAfterValue`. These events are useful for diagnosing page-table walk costs, STLB behavior, huge-page effects, and virtualization/EPT overhead called out in the walk-pending descriptions.

## Risks and Test Signals
The key risk is semantic precision around page sizes and walk states: `WALK_COMPLETED`, `WALK_COMPLETED_4K`, and `WALK_COMPLETED_2M_4M` share event codes with different masks, so mask accuracy determines whether derived analysis is valid. Sampling defaults are part of the generated alias and should not be accidentally dropped. Test signals include JSON validation, generated event strings with `period=` and `umask=`, `perf list` visibility, and workload smoke tests comparing TLB miss counters under 4K pages versus huge pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/virtual-memory.json -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/counter.json

## Purpose
This JSON file defines Granite Rapids PMU counter inventory metadata for perf. The complete 81-line file was read, containing 16 records. It does not define countable events; instead, it tells perf/generator consumers how many fixed and generic counters exist for the core and uncore units.

## Important APIs, Types, and Functions
The schema fields are `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. Units listed are `core`, `B2CMI`, `CHA`, `IMC`, `CXLCM`, `CXLDP`, `B2HOT`, `IIO`, `IRP`, `MDF`, `PCU`, `UBOX`, `UPI`, `B2UPI`, `B2CXL`, and `CHACMS`. The `core` unit has 4 fixed and 8 generic counters. Most uncore units have 0 fixed and 4 generic counters; `PCU` has 0 fixed and 6 generic counters. Some generic counts are JSON numbers and some are strings, so downstream parsing must tolerate both representations.

## Control Flow, State, and Persistence
This file is declarative metadata. It has no `EventName`, `EventCode`, or masks, so it is not an event alias table. The build pipeline reads it as part of the Granite Rapids PMU event directory so generated perf metadata can reflect counter capacity by PMU unit. There is no runtime mutation or persisted state beyond the checked-in JSON and generated tables.

## Dependencies and Integration Points
It depends on perf tooling that recognizes counter metadata records alongside event records. It integrates with Granite Rapids core and uncore event files by describing how many events can be scheduled simultaneously on each PMU unit. This matters for perf event grouping, multiplexing expectations, and validation of large event sets spanning core, CHA, IMC, IIO, CXL, UPI, and PCU units.

## Risks and Test Signals
The main risk is metadata drift relative to kernel PMU capabilities or hardware revisions. A wrong counter count can mislead scheduling decisions or user expectations about multiplexing. Mixed numeric/string JSON values for `CountersNumGeneric` are a compatibility risk if a stricter parser assumes one type. Test signals include JSON validation, successful `jevents.py` processing, generated metadata inspection, comparison with kernel-exposed PMU counter counts under `/sys/bus/event_source/devices`, and grouped `perf stat` tests that verify expected scheduling behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/floating-point.json

## Purpose
This JSON file defines Granite Rapids core floating-point PMU events for perf. The complete 242-line file was read, containing 28 event records. It exposes floating-point divider active cycles, FP assists, SSE/AVX transition assists, dispatched FP operations by execution port/vector alias, and retired FP arithmetic instruction classes including half-precision variants.

## Important APIs, Types, and Functions
The file uses `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, and optional `CounterMask`. There are no functions or classes. Event families are `FP_ARITH_INST_RETIRED` (12), `FP_ARITH_INST_RETIRED2` (7), `FP_ARITH_DISPATCHED` (6), `ASSISTS` (2), and `ARITH.FPDIV_ACTIVE` (1). All records target core counters `0,1,2,3,4,5,6,7`. `ARITH.FPDIV_ACTIVE` uses `CounterMask` `1`; dispatch port events include aliases between `PORT_0/1/5` and `V0/V1/V2`; retired arithmetic records separate scalar, packed single/double, vector aggregate, and FP16 half-precision classes.

## Control Flow, State, and Persistence
The file is consumed by the perf PMU event generator. `jevents.py` converts each record into a generated core PMU alias, maps `SampleAfterValue` to `period=`, `UMask` to `umask=`, and `CounterMask` to `cmask=`. Runtime perf commands use the aliases for counting or sampling FP-heavy workloads. The source JSON is static; generated C tables are the persistent build product.

## Dependencies and Integration Points
It depends on Granite Rapids core PMU support and perf's x86 model mapping. It integrates with HPC and vectorization analysis, compiler/codegen investigations, and assist diagnostics for FP pipelines. It also connects to Granite Rapids `counter.json`, since all events draw from the eight generic core counters when scheduled together.

## Risks and Test Signals
The main risks are alias duplication and mask aggregation semantics. The port and vector dispatch names are intentional aliases with identical encodings, so duplicate-looking definitions should not be removed without checking user-facing compatibility. Aggregate retired events such as `4_FLOPS`, `8_FLOPS`, `SCALAR`, and `VECTOR` use combined masks and can be misread as derived metrics even though they are raw PMU events. Test signals include JSON syntax validation, `jevents.py` generation, alias visibility in `perf list`, generated event strings with `period=` and `cmask=` for `ARITH.FPDIV_ACTIVE`, and workload checks using scalar, AVX2/AVX-512, and FP16 instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/floating-point.json -->
