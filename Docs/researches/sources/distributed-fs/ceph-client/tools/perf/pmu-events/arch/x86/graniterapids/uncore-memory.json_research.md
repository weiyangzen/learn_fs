# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-memory.json

## Purpose
This JSON file defines 94 Intel Granite Rapids integrated memory controller uncore PMU events for perf. It covers DRAM activation, CAS read/write counts for scheduler channels, refresh and self-refresh behavior, power-down and throttling cycles, read/write queue inserts and occupancy, and memory-controller clock events. The source was read as a complete 890-line JSON array.

## Important APIs, Types, and Functions
All entries use perf's x86 event JSON schema with `EventName`, `EventCode`, `BriefDescription`, `Counter`, `PerPkg`, `UMask`, and `Unit`. `Unit` is always `IMC`, `Counter` is consistently `0,1,2,3`, and `PerPkg` is consistently `1`. Two entries include `PublicDescription`, and many are flagged `Experimental: "1"`. The file has 94 unique event names and 30 unique event codes.

Important event families include `UNC_M_ACT_COUNT.*`, `UNC_M_CAS_COUNT_SCH0.*`, `UNC_M_CAS_COUNT_SCH1.*`, `UNC_M_CLOCKTICKS`, `UNC_M_HCLOCKTICKS`, `UNC_M_MNTCMD_REFRATE.*`, `UNC_M_MR4_2XREF_CYCLES.*`, `UNC_M_PDC_MR4ACTIVE_CYCLES.*`, `UNC_M_POWERDOWN_CYCLES.*`, `UNC_M_POWER_*`, `UNC_M_PRE_COUNT.*`, `UNC_M_RDB_*`, `UNC_M_RPQ_*`, `UNC_M_WPQ_*`, `UNC_M_SELF_REFRESH.*`, and `UNC_M_THROTTLE_*`. The naming encodes scheduler, pseudo-channel, DIMM, rank, and slot dimensions directly in the event name.

## Control Flow, State, and Persistence
The file has no direct control flow. During the perf build, `jevents.py` reads the JSON array and emits generated C event metadata. Runtime perf commands resolve aliases into IMC uncore PMU event selectors and collect package-scoped hardware counts.

The declarative state is the mapping from event aliases to raw event code/unit mask pairs plus counter and scope constraints. Many event names expose hardware substructure such as `SCH0`, `SCH1`, `PCH0`, `PCH1`, DIMM indices, ranks, and throttle slots. These dimensions are persistent metadata in the generated perf tables; observed counts are transient. Since these are memory-controller events, state is not tied to a task context and should be interpreted with system-wide collection semantics.

## Dependencies and Integration Points
Dependencies include the perf PMU JSON schema, Granite Rapids model selection, Intel IMC event definitions, `jevents.py`, and kernel uncore IMC PMU support. The file integrates with `perf list` for IMC event discovery and `perf stat` for socket/package-level memory-controller analysis. It is a natural integration partner for uncore interconnect events, IIO traffic events, and power events when diagnosing bandwidth, throttling, refresh overhead, or memory power-management behavior.

There are no metric expressions here. Any bandwidth or utilization metric must be built externally from CAS counts, queue occupancy, clockticks, and platform-specific scaling factors such as channel width and memory transfer rate.

## Risks and Test Signals
Risks include experimental event semantics, channel/pseudo-channel naming drift, incorrect unit masks for aggregate versus channel-specific counts, and mixing occupancy/cycle events with transaction counts. Power and throttle events can be highly platform-policy dependent, so they may be valid but zero or hard to interpret on systems without the relevant throttling or memory power states.

Test signals include JSON validation, successful event-table generation, `perf list` visibility for `UNC_M_CAS_COUNT_SCH*`, `UNC_M_RPQ_*`, `UNC_M_WPQ_*`, and throttle events, and hardware smoke tests under memory read/write stress. Plausibility checks should compare read-heavy workloads against `RD` events, write-heavy workloads against `WR` events, and idle or low-power scenarios against self-refresh and power-down residency events.
