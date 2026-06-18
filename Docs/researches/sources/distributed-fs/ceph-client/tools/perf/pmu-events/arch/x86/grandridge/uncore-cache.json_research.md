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
