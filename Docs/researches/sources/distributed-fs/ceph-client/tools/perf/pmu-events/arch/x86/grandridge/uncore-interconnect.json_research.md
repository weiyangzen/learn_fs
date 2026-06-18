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
