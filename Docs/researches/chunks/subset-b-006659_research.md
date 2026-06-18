# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-interconnect.json lines 1-6508

## Scope

This chunk covers lines 1-6508 of the Emerald Rapids x86 uncore interconnect PMU event table. The underlying file is a JSON array of 728 event objects; this chunk contains 620 complete `"EventName"` entries, from `UNC_I_CACHE_TOTAL_OCCUPANCY.MEM` through `UNC_UPI_RxL_ANY_FLITS.SLOT2`, and then the beginning of the next object at lines 6506-6508. The next complete event, `UNC_UPI_RxL_BASIC_HDR_MATCH.NCB`, starts after this chunk and must be handled by the following chunk/merge lane.

## Purpose

The file is static PMU metadata consumed by perf's `pmu-events` generation pipeline. It describes Intel Emerald Rapids uncore interconnect events for IRP, M2M, M3UPI, MDF, UPI, and later UBOX units. Each JSON object maps a user-facing perf event alias to hardware encoding fields and documentation:

- `EventName` is the perf alias, using Intel-style uncore names such as `UNC_M2M_IMC_READS.CH0_TO_PMM`.
- `EventCode` and `UMask` encode the hardware selector and unit mask.
- `Counter` restricts which counters can count the event.
- `Unit` identifies the PMU block and is converted by `jevents.py` into PMU names such as `uncore_irp`, `uncore_m2m`, `uncore_m3upi`, `uncore_mdf`, and `uncore_upi`.
- `BriefDescription` and optional `PublicDescription` become short and long descriptions shown by perf.
- `PerPkg` marks package-scoped uncore events.
- `Experimental` labels events that perf should preserve as experimental metadata.

There is no executable logic in this source file. Its behavior is defined by downstream parsers and generated C tables.

## Event Families In This Chunk

The first IRP section describes inbound request path cache and fabric behavior: cache occupancy, clock ticks, FAF fullness/inserts/occupancy/transactions, aggregate IRP inbound/outbound insert counts, misc fast/slow path transfer states, snoop response categories, write prefetches, TxC queue inserts/occupancy/full cycles, TxR2 credit stalls, and TxS request/data insert/occupancy counters.

The M2M section is broad and models memory-to-memory and memory-controller related interconnect traffic. It includes M2M clock ticks, direct-to-core and direct-to-UPI override/not-taken reasons, directory hit/miss/update states, egress ordering, IMC read/write traffic split by channel and destination, prefetch CAM drops/merges/inserts/occupancy/response misses, RxC inserts and occupancy, tag hit/miss states, TGR credits, tracker occupancy/inserts, WPQ flush/no-credit states, and write tracker posted/nonposted occupancy and inserts.

The M3UPI section is the largest part of this chunk. It covers M3-to-UPI bridge behavior: CHA AD credit-empty states, M3UPI clocks, direct-to-core/direct-to-UPI sends, M2 BL credit-empty states, multi-slot receives, RxC arbitration loss/no-credit/no-request conditions for VN0 and VN1, bypass and credit occupancy conditions, header/data flit generation and not-sent reasons, held/packing miss conditions, VNA credit states, TxC AD/AK/BL flow queue arbitration/inserts/occupancy, peer UPI credit-empty states, VN0/VN1 credits used and no-credit events, writeback pending/occupancy comparisons, and XPT prefetch arbitration/arrival/bypass/flit/loss outcomes.

The MDF section in this chunk describes CRS TxR inserts and virtual-channel bounces across AD, AK, AKC, BL, and IV traffic classes plus fast assertion counters for selected AD/BL conditions.

The UPI portion begins at line 6092 and continues through complete `UNC_UPI_RxL_ANY_FLITS` events at line 6505. It includes UPI clockticks, direct attempts, FlowQ no-VNA-credit conditions, power/L1/PHY cycle and request/nack counters, M3 bypass/RXQ/credit-return blocking reasons, request slot-2 traffic from M3, RxL0/RxL0P power cycles, and RxL flit classifications for data, LLCRD, LLCTRL, null, protocol header, and slots 0-2.

## Important Data Fields

The chunk uses a compact, repeated schema rather than local functions or types. The important fields are:

- `EventName`: stable event alias. `jevents.py` lowercases it when building internal generated tables, but perf list output can still present canonical names through generated metadata.
- `EventCode`: selector value. Some families share an event code and use different `UMask` values to distinguish subevents.
- `UMask`: subevent mask. Many adjacent entries differ only by UMask and suffix, especially virtual-network, channel, and slot breakdowns.
- `Counter`: allowed counter list. IRP events in this chunk generally use `0,1`; M2M and M3UPI often use `0,1,2,3`; some UPI entries also use all four counters.
- `Unit`: routes the event to the appropriate uncore PMU namespace through `unit_to_pmu()` in `pmu-events/jevents.py`.
- `PerPkg`: appears throughout and indicates package-level aggregation semantics.
- `Experimental`: common in this chunk, especially for detailed interconnect diagnostics. Consumers should not infer that every event is stable ABI.
- `BriefDescription`/`PublicDescription`: documentation strings. Several events have only brief descriptions; perf tests explicitly account for missing public descriptions by comparing public description fallback behavior.

## Generation And Control Flow

Build integration is data-driven:

1. `tools/perf/pmu-events/Build` lists JSON event files under `pmu-events/arch` as dependencies for generated `$(OUTPUT)pmu-events/pmu-events.c`.
2. The build rule invokes `pmu-events/jevents.py` with the selected architecture/model and output arch directory.
3. `jevents.py` reads each JSON object, parses numeric fields such as `EventCode`, `ConfigCode`, and `UMask`, maps `Unit` to a PMU name, stores descriptions, package flags, metric fields, filters, and experimental/deprecated metadata, then emits generated C tables.
4. Runtime perf code uses those generated tables to populate PMU aliases, metric/event lookup, Python dictionaries, and `perf list` output. `builtin-list.c` can print event metadata back as JSON-like output with `Unit`, `EventName`, `BriefDescription`, `PublicDescription`, and encoding fields.

There is no branching or state transition in this JSON itself. The effective control flow is the generator pipeline plus perf runtime alias lookup.

## State And Persistence

The source file is persistent metadata checked into the perf source tree. It does not maintain runtime state. Its values are compiled into generated `pmu-events.c` during build, after which perf treats them as read-only event table data. Runtime counter state is held by kernel PMU drivers and perf sessions, not by this JSON.

The `PerPkg` flags affect how users and tooling should interpret counts across packages. Occupancy-style events, credit-empty events, and cycle-not-empty/full events are especially sensitive to aggregation mode and sampling interval interpretation because the JSON only declares raw encodings and descriptions, not formulas or normalization.

## Dependencies And Integration Points

Primary dependencies are perf's PMU event tooling:

- `pmu-events/jevents.py` is the schema consumer and generated C producer.
- `pmu-events/Build` wires the JSON file into the build when Emerald Rapids/x86 PMU events are generated.
- `pmu-events/pmu-events.h` defines the generated table interfaces used by perf.
- `util/pmu.c` and `util/pmu.h` consume generated event tables for PMU alias discovery.
- `builtin-list.c` exposes the generated metadata through `perf list`, including JSON-style listing output.
- `tests/pmu-events.c` verifies generated event tables and alias behavior against test fixtures.
- `pmu-events/metric.py` and `intel_metrics.py` can scan event names when building or validating derived metrics, although this file is event metadata rather than a metric formula file.

The source is also implicitly coupled to Intel Emerald Rapids uncore PMU hardware documentation and to Linux kernel uncore PMU naming. A bad `Unit` string or stale hardware encoding can make the generated perf alias target the wrong PMU or fail to match available sysfs PMUs.

## Risks And Edge Cases

The chunk boundary is inside a JSON object. Lines 6506-6508 only contain the start of `UNC_UPI_RxL_BASIC_HDR_MATCH.NCB`; chunk-level research must not treat that event as complete until the following chunk provides the remaining fields.

Because many entries differ only by `UMask`, suffix, channel, slot, VN, or traffic class, copy/paste drift is a major risk. Examples include CH0/CH1 IMC read/write variants, VN0/VN1 M3UPI arbitration variants, and RxL flit-slot variants. A single wrong mask can silently expose an alias that counts a different hardware condition.

Descriptions are uneven. Some events have full `PublicDescription`; many detailed M3UPI and UPI diagnostic events only repeat the event name in `BriefDescription`. This is acceptable to the generator but lowers usability of `perf list` and complicates validation by humans.

`Experimental` is frequent and should be preserved. Tooling that filters or hides experimental events could make many diagnostics absent even though the raw encodings exist.

Counter constraints matter. Using an event on a counter not listed in `Counter` may fail scheduling or produce wrong programming constraints. Since the JSON is the source of allowed counters for generated metadata, incorrect counter sets have runtime impact.

The unit-to-PMU mapping is convention-based. Unknown units default to `uncore_<lowercase unit>` in `jevents.py`; that is useful for new uncore blocks but risky if a typo creates a plausible-looking PMU name that does not match the kernel.

## Test Signals

Useful validation signals for this chunk include:

- `jq` parses the full JSON file as an array, and line-aware chunking confirms 620 complete `EventName` entries through line 6508.
- The complete file reports expected unit distribution, including IRP, M2M, M3UPI, MDF, UPI, and UBOX; this chunk reaches UPI and not the later complete UBOX tail.
- `perf` build generation should regenerate `pmu-events.c` without `jevents.py` parse failures.
- `perf test pmu-events` should continue passing generated event table and alias checks.
- `perf list --json` or equivalent listing for an Emerald Rapids-capable build should surface aliases with expected units/descriptions/encodings.
- Spot checks should compare representative adjacent aliases, for example `UNC_M2M_IMC_READS.CH0_*` vs `CH1_*`, `UNC_M3UPI_RxC_ARB_* VN0` vs `VN1`, and `UNC_UPI_RxL_ANY_FLITS.*`, to catch swapped masks or counters.

## Open Cross-Chunk Notes

The final per-file report should merge this chunk with the remaining lines 6509-7626. In particular, it should account for the rest of the UPI receive/transmit/header-match families and the final UBOX events that are outside this chunk. The merge lane should also avoid double-counting the partial object that starts at lines 6506-6508.
