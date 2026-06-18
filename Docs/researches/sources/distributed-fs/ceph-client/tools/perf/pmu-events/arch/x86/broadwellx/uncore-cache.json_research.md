# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-cache.json

## Purpose

This file is a Broadwell-EP/EX (`broadwellx`) perf PMU event catalog for uncore cache and home-agent activity. It is not executable code; it is structured input to `tools/perf/pmu-events/jevents.py`, which turns JSON event records into generated `pmu-events.c` tables compiled into `perf`. The matching CPU map row is `GenuineIntel-6-4F,v23,broadwellx,core` in `arch/x86/mapfile.csv`, so these aliases are selected for Intel family 6 model 0x4f systems.

The file contains 399 event objects over 3,965 lines. The events are split between 179 `CBOX` records and 220 `HA` records. `CBOX` entries describe cache-box / LLC / ring-stop behavior such as LLC lookups, victims, TOR inserts and occupancy, RxR/TxR queues, ring use, and CBo credit pressure. `HA` entries describe home-agent behavior such as directory lookups and updates, HITME lookup/hit states, IMC reads/writes, snoops, tracker occupancy, TAD regions, TxR scheduler activity, and queue credit stalls.

## Schema And Event API

Each array entry is the public API exposed to perf users as a symbolic event alias. The fields used in this file are:

- `EventName`: required alias name, for example `UNC_C_TOR_INSERTS.MISS_OPCODE` or `UNC_H_REQUESTS.READS_LOCAL`. `jevents.py` lowercases this into `JsonEvent.name`, so user-visible matching is case-insensitive in practice.
- `EventCode`: hardware event selector. Two clocktick events omit this field and rely on an encoded zero event value.
- `UMask`: subevent mask appended as `umask=<value>` when non-zero.
- `Unit`: logical hardware unit. `jevents.py` maps `CBOX` to generated PMU name `uncore_cbox` and `HA` to `uncore_ha`.
- `Counter`: allowed counters for the unit. Most events allow `0,1,2,3`; occupancy-style `CBOX` events such as `UNC_C_RxR_OCCUPANCY.*`, `UNC_C_SBO_CREDIT_OCCUPANCY.*`, and `UNC_C_TOR_OCCUPANCY.*` are restricted to counter `0`; several HA IOT/CTS events allow `0,1,2`.
- `BriefDescription`: short text displayed by `perf list` and exposed via perf Python helpers.
- `PublicDescription`: longer help text. Many descriptions document hardware caveats, required filters, and interpretation pitfalls.
- `Filter`: extra filter terms appended to the generated event encoding, for example `filter_opc=0x182`, `filter_tid=0x3e`, `filter_nc=1`, or `filter_state=0x1`.
- `ScaleUnit`: semantic unit for scaled output. Several line-count events use `64Bytes`; most events have no scale unit.
- `PerPkg`: all events use `"1"`, marking package-level aggregation semantics for these uncore counters.

Representative generated encodings include `event=0x35,umask=0x3,filter_opc=0x182` for `LLC_MISSES.DATA_READ`, `event=0x34,umask=0x11,filter_state=0x1` for `UNC_C_LLC_LOOKUP.ANY`, and `event=0x1,umask=0x1` for `UNC_H_REQUESTS.READS_LOCAL`.

## Important Event Families

The first CBOX group provides derived friendly aliases for LLC misses and references. These use `EventCode` `0x35` with opcode filters to distinguish data reads, code LLC prefetches, RFO prefetches, PCIe reads/writes, MMIO, uncacheable reads, streaming stores, and partial/full-line writes. These aliases depend heavily on `filter_opc` and, for PCIe non-snoop or full-line write distinctions, `filter_tid`.

The core CBOX families are `UNC_C_LLC_LOOKUP.*`, `UNC_C_LLC_VICTIMS.*`, `UNC_C_TOR_INSERTS.*`, and `UNC_C_TOR_OCCUPANCY.*`. `UNC_C_LLC_LOOKUP.*` documents a non-standard filtering equation: bit 0 in the umask and an FMESI state selection must be programmed or the event counts nothing. `UNC_C_TOR_INSERTS.*` counts transaction-ordering-register insertions across all, miss, local, remote, NID-qualified, opcode-qualified, eviction, and writeback subevents. `UNC_C_TOR_OCCUPANCY.*` mirrors these categories as counter-0 occupancy events.

The CBOX interconnect and queue families include `UNC_C_RING_{AD,AK,BL,IV}_USED.*`, `UNC_C_RING_BOUNCES.*`, `UNC_C_RING_SINK_STARVED.*`, `UNC_C_RxR_*`, `UNC_C_TxR_*`, and CBo/SBo credit events. These expose ring direction, even/odd polarity, retry causes, queue inserts, queue occupancy, internal/external starvation, and AD/BL credit acquisition/occupancy.

The HA groups cover home-agent request routing and coherency. Key families are `UNC_H_REQUESTS.*`, `UNC_H_DIRECTORY_LOOKUP.*`, `UNC_H_DIRECTORY_UPDATE.*`, `UNC_H_HITME_LOOKUP.*`, `UNC_H_HITME_HIT.*`, `UNC_H_HITME_HIT_PV_BITS_SET.*`, `UNC_H_SNOOP_*`, `UNC_H_SNP_RESP_RECV_LOCAL.*`, `UNC_H_TRACKER_*`, `UNC_H_OSB*`, and `UNC_H_TAD_REQUESTS_G{0,1}.*`. The HA section also includes memory-controller-facing reads/writes, RPQ/WPQ credit stalls by channel, QPI ingress credit stalls, IOT backpressure/CTS counters, and TxR scheduler cycles/inserts/fullness.

## Control Flow And Integration

Build-time control flow starts with the perf PMU events build rules running `pmu-events/jevents.py` before linking `perf`. `read_json_events(path, topic)` loads this file through Python `json.load(..., object_hook=JsonEvent)`. `JsonEvent.__init__` converts each JSON object into normalized generated-data fields:

- `EventName` becomes lowercase `name`.
- `BriefDescription` and `PublicDescription` become escaped short and long descriptions.
- `Unit` becomes a Linux PMU selector through `unit_to_pmu`; for this file, `CBOX` maps to `uncore_cbox` and `HA` maps by the generic fallback to `uncore_ha`.
- `EventCode`, `UMask`, and recognized JSON fields are joined into a comma-separated perf event term string.
- `Filter` is appended verbatim to the event term string.
- `ScaleUnit` becomes the generated unit string, and `PerPkg` is preserved as package aggregation metadata.

The generated C data uses `struct pmu_event` / `struct pmu_events_table` and is selected by the CPU mapping table. Runtime perf code then finds the matching events table for the active PMU/CPU and creates `struct perf_pmu_alias` records. PMU name matching for uncore devices ignores numeric suffixes and supports wildcard matching, allowing one JSON unit such as `uncore_cbox` to match system PMU instances such as per-socket or per-box uncore devices.

User-facing integration points are `perf list`, `perf stat -e <alias>`, parser alias expansion, perf Python dictionaries, and PMU event tests. The aliases in this file are also likely consumed indirectly by BroadwellX metric JSON files when metric expressions reference cache, ring, home-agent, or memory-request events.

## State And Persistence Behavior

This file has no runtime state, mutation, persistence, or I/O of its own. Its persistent effect is the generated event metadata compiled into the perf binary. Changes to names, event codes, umasks, filters, units, descriptions, or scale units alter generated `pmu-events.c`, then alter runtime alias availability and the raw hardware encodings perf programs through `perf_event_open`.

Because all records set `PerPkg` to `1`, these events persist as package-level uncore aliases rather than per-core aliases. Counter restrictions are declarative only; the actual enforcement depends on perf's PMU format and scheduling logic for the corresponding uncore PMU.

## Dependencies

The JSON depends on the perf PMU-events schema implemented by `jevents.py`, on the x86 `mapfile.csv` row for `broadwellx`, and on Linux sysfs PMU names/formats for Intel uncore CBOX and HA devices. The generated encodings assume hardware support for BroadwellX event selectors, umasks, filter fields such as `filter_opc`, `filter_tid`, `filter_nc`, and `filter_state`, and unit PMU names compatible with `uncore_cbox` / `uncore_ha`.

The descriptive content is effectively hardware documentation embedded in the source tree. Several event meanings depend on BroadwellX-specific topology and uncore behavior, including ring direction reversal between chip halves, CBo global control FMESI state bits, TOR opcode/NID filters, and HA tracker or HITME state encodings.

## Risks And Maintenance Notes

The highest-risk fields are `Filter`, `UMask`, and `Unit`. `Filter` is appended verbatim by `jevents.py`; a typo can produce an alias that builds but cannot be programmed on the target PMU. `Unit` names determine PMU routing; changing `CBOX` or `HA` would redirect aliases or make them invisible to the intended uncore devices. `UMask` values encode subevents and composite masks, so a one-character error can silently count a different hardware condition.

Some aliases are derived convenience names over the same base event, especially `LLC_MISSES.*`, `LLC_REFERENCES.*`, `UNC_C_TOR_INSERTS.*`, `UNC_C_TOR_OCCUPANCY.*`, and HA HITME groups. Duplicate event codes are expected, but duplicate or conflicting `EventName` values would damage alias lookup. There are two events without `EventCode` (`UNC_C_CLOCKTICKS`, `UNC_H_CLOCKTICKS`), which should be checked carefully if schema validation changes because `jevents.py` currently treats a missing event code as zero.

Descriptions contain important operational caveats. For example, `UNC_C_LLC_LOOKUP.*` says missing required state/umask setup can count nothing, and ring-use descriptions explain BroadwellX ring direction dependence. Losing these descriptions would not break builds but would remove critical guidance for performance analysis.

The file is broad and hand-maintained data, so drift against Intel documentation or Linux uncore PMU format files is a realistic risk. The presence of `Counter: "0"` on occupancy records also means test coverage should include counter-constraint-sensitive events, not only ordinary programmable events.

## Test Signals

Useful validation signals for this file are:

- JSON parses cleanly: `jq length sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-cache.json` returns `399`.
- Schema keys remain within the expected set used here: `BriefDescription`, `Counter`, `EventCode`, `EventName`, `Filter`, `PerPkg`, `PublicDescription`, `ScaleUnit`, `UMask`, and `Unit`.
- Build generation with `jevents.py` succeeds for x86 PMU events and produces BroadwellX entries without duplicate-name or invalid-field failures.
- Perf PMU event tests, especially `tools/perf/tests/pmu-events.c`, continue to pass because they exercise generated table iteration, lookup, alias conversion, and generated-vs-expected event comparisons.
- Runtime smoke tests on BroadwellX hardware should verify representative aliases from both units: `LLC_MISSES.DATA_READ`, `UNC_C_LLC_LOOKUP.ANY`, `UNC_C_TOR_INSERTS.MISS_OPCODE`, `UNC_C_TOR_OCCUPANCY.LLC_DATA_READ`, `UNC_H_REQUESTS.READS_LOCAL`, `UNC_H_HITME_LOOKUP.ALL`, and `UNC_H_SNOOP_RESP.RSPS`.
- `perf list` should show these aliases under uncore PMUs, and `perf stat` should either program valid uncore events or produce clear PMU availability errors on non-BroadwellX systems.
