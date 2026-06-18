# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/uncore-memory.json

## Purpose
Defines the Sierra Forest integrated memory controller PMU event catalog for perf. The 90-entry JSON array describes `UNC_M_*` aliases for DRAM command activity, memory queue inserts and occupancy, read/write CAS counts by subchannel, self-refresh, power-down, MR4 thermal refresh behavior, and memory throttling.

## Important APIs, Types, And Event Groups
The public contract is perf's PMU event JSON schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, `PerPkg`, and `Unit`. `Unit` is consistently `IMC`, routing events to integrated memory controller uncore PMUs, and `Counter` generally allows counters `0,1,2,3`. `PublicDescription` appears on selected entries where extra user-facing explanation is needed. Roughly half the entries are marked `Experimental`.

Major groups include `UNC_M_ACT_COUNT` for activate commands, `UNC_M_CAS_COUNT_SCH0` and `UNC_M_CAS_COUNT_SCH1` for read/write CAS operations per subchannel, `UNC_M_PRE_COUNT` for precharge operations, `UNC_M_RPQ/WPQ/RDB_INSERTS` and occupancy events for request/write/read-data buffers, `UNC_M_POWERDOWN_CYCLES`, `UNC_M_SELF_REFRESH`, `UNC_M_MR4_2XREF_CYCLES`, `UNC_M_PDC_MR4ACTIVE_CYCLES`, and throttle-level counters such as low/mid/high/critical cycles.

## Control Flow
The file has declarative parse-time flow only. Perf's build pipeline reads the array, turns each object into an event table row, and preserves event names as aliases. During a measurement, perf maps an alias to the IMC PMU and passes event code and mask fields to kernel perf. Subchannel and command-class distinctions are encoded as separate aliases rather than runtime branches.

## State And Persistence
The persistent state is static event metadata. The file does not store measurement results. At runtime, state lives in per-PMU kernel event descriptors and hardware IMC counters. Package and channel topology determine how many IMC PMU instances can be opened by perf; this JSON only supplies alias metadata.

## Dependencies And Integration Points
This catalog depends on Sierra Forest IMC PMU kernel support and perf's generated event table infrastructure. It integrates with platform topology because `IMC` events are uncore and package/channel scoped, not thread scoped. It also integrates with perf expression and listing paths through descriptive fields, letting users discover memory-controller aliases by category and event name.

## Risks
The biggest correctness risk is mismatching command class masks, especially in dense CAS subchannel families where read, write, underfill, auto-precharge, and regular variants differ only by `UMask`. Experimental thermal, throttling, and queue occupancy events may have caveats or changing documentation. Users can misinterpret occupancy events as transaction counts; reports should distinguish count events from cycle/occupancy events.

## Test Signals
Validate JSON syntax with `jq empty` and generated perf table builds. On supported hardware, `perf list` should expose `UNC_M_*` aliases under IMC. Runtime checks should open representative activate, CAS read/write, queue insert, queue occupancy, self-refresh, and throttle events. Cross-checking read/write CAS counters against memory bandwidth workloads is a practical semantic signal.
