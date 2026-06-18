# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-memory.json

## Purpose

`uncore-memory.json` is the Emerald Rapids uncore memory PMU catalog for perf. It contains 403 package-level memory events split across `iMC`, `MCHBM`, and `M2HBM` units, covering integrated memory-controller traffic, HBM controller traffic, directory/coherency behavior, queues, tracker occupancy, prefetch CAM behavior, power-management memory states, ECC, refresh, precharge, and PMM-side queues. The file is data, not executable code, but it is a central input to perf's generated event tables.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects. Common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, `PublicDescription`, and optional qualifiers such as `Experimental`, `FCMask`, and `PortMask`. `Unit` is the PMU selector: 161 events use `iMC`, 67 use `MCHBM`, and 175 use `M2HBM`. Most events are programmable on counters `0,1,2,3`.

Major event families include `UNC_M_CAS_COUNT.*`, `UNC_M_ACT_COUNT.*`, `UNC_M_PRE_COUNT.*`, `UNC_M_DRAM_REFRESH.*`, `UNC_M_POWER_*`, `UNC_M_RDB_*`, `UNC_M_RPQ_*`, `UNC_M_WPQ_*`, `UNC_M_SB_*`, `UNC_M_PMM_*`, `UNC_MCHBM_CAS_COUNT.*`, `UNC_MCHBM_ACT_COUNT.*`, `UNC_MCHBM_PRE_COUNT.*`, `UNC_M2HBM_IMC_READS.*`, `UNC_M2HBM_IMC_WRITES.*`, `UNC_M2HBM_DIRECTORY_*`, `UNC_M2HBM_DIRECT2CORE_*`, `UNC_M2HBM_DIRECT2UPI_*`, `UNC_M2HBM_PREFCAM_*`, `UNC_M2HBM_TRACKER_*`, and `UNC_M2HBM_WR_TRACKER_*`.

## Control Flow and Data Flow

There is no local control flow. Perf PMU tooling parses this JSON, generates architecture-specific event aliases, and maps selected aliases to uncore PMU event encodings at runtime. The data flow is from static JSON rows into perf list/stat metadata, then into programmed uncore counters on the selected package. `PerPkg` marks these as package-scoped measurements rather than thread-local core events.

The families form analysis flows: CAS and request counters estimate read/write bandwidth; ACT/PRE/page-policy counters describe DRAM/HBM row behavior; RPQ/WPQ/RDB/SB queues expose pressure and occupancy; directory and direct-to-core/direct-to-UPI events expose HBM coherency routing; PMM and power rows describe persistent-memory and memory power-management side effects.

## State and Persistence Behavior

The only persistent state is the static event metadata in the repository. Runtime counter values are produced by perf sessions and are not stored here. Occupancy and cycle events represent time-integrated hardware states, while insert/count events represent transactions. Experimental rows persist as event aliases but should be treated as less stable contracts. `PerPkg` and `Unit` are important persistence semantics because they determine aggregation boundaries and PMU instance selection.

## Dependencies and Integration Points

This file depends on Emerald Rapids uncore PMU support in the Linux perf tooling and kernel PMU drivers. It integrates with `perf list`, `perf stat`, memory bandwidth diagnostics, HBM/DRAM balancing analysis, coherency routing investigations, PMM queue analysis, and platform power/thermal studies. It complements `uncore-power.json` by exposing memory-side power states and complements core cache/TLB events by measuring controller and fabric behavior after requests leave the core.

## Risks and Edge Cases

The largest risk is semantic misaggregation: package-level uncore counts include all cores and processes on a package, not just the profiled task. Counters in different units cannot be freely summed without understanding topology. Occupancy/cycle events and transaction events use different units and should not be mixed as raw counts. HBM and DRAM names are similar but refer to different PMU units. Many `M2HBM` rows are marked `Experimental`, so downstream tests should tolerate platform or kernel support gaps. Events using `FCMask` or `PortMask` depend on perf preserving the mask fields exactly. Bandwidth conversions from CAS/read/write events need the correct transaction width and channel interpretation.

## Test Signals

Useful validation starts with JSON parse success and generated perf event-table build success. Runtime smoke tests should verify `perf list` exposes `iMC`, `MCHBM`, and `M2HBM` aliases on matching Emerald Rapids systems. Streaming read/write workloads should move CAS, read, and write counters; random-access workloads should affect activation/precharge and queue-pressure rows; HBM-capable workloads should move `MCHBM`/`M2HBM` counters; power-management scenarios should affect `UNC_M_POWER_*`; and idle baselines should keep transaction counters low while clocktick counters advance.
