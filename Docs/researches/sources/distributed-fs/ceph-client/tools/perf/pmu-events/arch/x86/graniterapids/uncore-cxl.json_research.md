# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-cxl.json

## Purpose

`uncore-cxl.json` is the Granite Rapids uncore CXL PMU topic file. It defines three package-scoped events for CXL-related uncore units: B2CXL clockticks, CXLCM receive-side memory data packing buffer inserts, and CXLDP transmit-side M2S data AGF inserts. These records give perf symbolic aliases for low-level CXL fabric/data-path counters.

The file is a small declarative JSON input to perf's PMU event generation. It contains no functions or executable control flow.

## Important APIs, Types, And Event Fields

The three records follow the perf PMU JSON event schema:

- `UNC_B2CXL_CLOCKTICKS`: uses `Unit` `B2CXL`, `EventCode` `0x01`, counters `0,1,2,3`, `PortMask` `0x000`, and `PerPkg` `1`.
- `UNC_CXLCM_RxC_PACK_BUF_INSERTS.MEM_DATA`: uses `Unit` `CXLCM`, `EventCode` `0x41`, `UMask` `0x10`, counters `4,5,6,7`, and `PerPkg` `1`.
- `UNC_CXLDP_TxC_AGF_INSERTS.M2S_DATA`: uses `Unit` `CXLDP`, `EventCode` `0x02`, `UMask` `0x20`, counters `0,1,2,3`, and `PerPkg` `1`.

Schema fields of note are `Unit`, which binds each alias to a specific uncore PMU type; `PerPkg`, which marks package-level scope; `Counter`, which differs between the CXLCM record and the other two records; and `PortMask`, which is present only on the B2CXL clocktick event and is translated by `jevents.py` to a channel-mask config term.

## Control Flow

The build path is the standard perf PMU event path. `pmu-events/Build` collects JSON inputs under `pmu-events/arch/x86`, then `jevents.py` parses this file, converts `Unit` names to Linux PMU identifiers, maps fields such as `PortMask`, `EventCode`, and `UMask` into generated event strings, and emits C table entries. The Granite Rapids mapfile row selects this directory for CPU IDs matching `GenuineIntel-6-A[DE]`.

At runtime, perf resolves these generated aliases against available uncore PMU instances. Users can request the aliases by name instead of configuring B2CXL, CXLCM, or CXLDP event selectors manually.

## State And Persistence Behavior

The JSON is static source metadata. It does not store runtime samples or maintain mutable state. Once generated into perf, it persists as alias definitions in the binary. Runtime behavior depends on the kernel exposing the relevant uncore CXL PMU devices and on the package topology present on the system.

## Dependencies And Integration Points

This file depends on Granite Rapids CXL uncore PMU support and perf's event-generation schema. It integrates with `uncore-cache.json` because CHA TOR records include CXL-hit/miss and `CXL_ACC` traffic views, while this file provides counters from dedicated CXL units. It also integrates with any memory/CXL performance workflows that correlate CXL data path activity with core stalls, LLC/TOR traffic, or memory-controller activity from sibling topic files.

## Risks And Edge Cases

The small number of records makes schema drift easy to spot, but each event is unit-specific. A wrong `Unit` value would bind an alias to the wrong PMU or make it disappear. The `Counter` split is important: `UNC_CXLCM_RxC_PACK_BUF_INSERTS.MEM_DATA` is restricted to counters `4,5,6,7`, unlike the B2CXL and CXLDP entries. If perf scheduling or documentation assumes all uncore CXL events use counters `0,1,2,3`, this record may fail to schedule in groups.

Another edge case is platform availability. A Granite Rapids CPU may match the event table while a given machine configuration lacks exposed CXL devices or PMU instances. In that case the alias can exist in generated metadata but not be schedulable on a specific host.

## Test Signals

Validation should include JSON parsing, x86 `jevents.py` generation, and checking generated aliases for all three event names. On suitable Granite Rapids hardware, `perf list` should expose B2CXL, CXLCM, and CXLDP aliases when the kernel exposes those PMUs. Runtime smoke tests should schedule `UNC_B2CXL_CLOCKTICKS` and one data-path insert event, with a separate group test for the CXLCM counter range constraint.
