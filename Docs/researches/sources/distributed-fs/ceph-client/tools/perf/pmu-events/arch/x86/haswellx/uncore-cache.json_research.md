# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-cache.json

## Purpose

This file is a perf PMU event description table for Intel Haswell-EP/Haswell-EX (`haswellx`) uncore cache-related monitoring. It is not executable code; it is build-time JSON consumed by `tools/perf/pmu-events/jevents.py` to generate C event tables that perf uses for event alias lookup, `perf list`, and event encoding when running on matching x86 CPUs.

The file contains 398 event records. The records cover two uncore PMU units:

- `CBOX`: 180 events for cache box behavior, including LLC lookups, LLC misses/references, victims, LRU state, ring usage, ingress/egress queues, TOR inserts, and TOR occupancy.
- `HA`: 218 events for home-agent/cache-coherence and memory-facing behavior, including directory lookups/updates, HitMe cache lookups/hits, QPI/iMC credit pressure, snoop responses, request classes, tracker occupancy, and ring/egress usage.

Although the filename is `uncore-cache.json`, the content also includes a substantial `UNC_H_*` home-agent section. That makes the file broader than pure CBOX cache events and important for Haswellx uncore performance investigations that span LLC, coherency, ring fabric, HA trackers, and memory-controller ingress pressure.

## Data Model and Important Fields

Each top-level array element is an event definition. The observed keys are:

- `EventName`: public perf alias, such as `LLC_MISSES.DATA_READ`, `UNC_C_TOR_OCCUPANCY.MISS_OPCODE`, or `UNC_H_REQUESTS.READS_LOCAL`.
- `EventCode`: raw uncore event select value. Two clocktick aliases, `UNC_C_CLOCKTICKS` and `UNC_H_CLOCKTICKS`, intentionally omit it.
- `UMask`: subevent mask. Twelve records omit it, mostly whole-unit, clock, or special control-style events.
- `BriefDescription`: short text shown by perf list/help paths.
- `PublicDescription`: longer user-facing semantics, present for most but not all events.
- `Counter`: allowed counter indexes. Most records use `0,1,2,3`; occupancy-style events often use only `0`; some HA IOT records use `0,1,2`.
- `Unit`: PMU unit selector, either `CBOX` or `HA`.
- `PerPkg`: always `"1"` in this file, marking these aliases as package-scoped uncore events.
- `Filter`: optional extra term string for events that require programmed uncore filter MSR fields. There are 18 filtered records, mainly opcode, node-id, target-id, and non-coherent qualifiers.
- `ScaleUnit`: optional reporting unit. There are 21 records with `64Bytes`, mostly data-volume-style LLC/TOR/victim events.

During generation, `jevents.py` maps these JSON fields into `struct pmu_event` fields declared in `pmu-events/pmu-events.h`: `EventName` becomes `name`, derived encoding terms become `event`, `BriefDescription` becomes `desc`, `PublicDescription` becomes `long_desc`, topic comes from the JSON filename, `Unit`/`ScaleUnit` contribute PMU matching and display unit data, and `PerPkg` becomes the boolean package aggregation flag.

## Event Families

The CBOX half defines:

- LLC miss/reference aliases derived from `UNC_C_TOR_INSERTS` opcode-filtered events, including code/data prefetches, demand data reads, RFO prefetches, PCIe reads/writes, MMIO, and uncacheable reads.
- LLC lookup and victim state counters, including FMESI-like state selection and NID-qualified variants.
- Ring usage on AD/AK/BL/IV rings, bounce counts, sink starvation, and source throttling.
- Ingress queue inserts, occupancy, internal/external starvation, and retry reasons for IPQ/IRQ/ISMQ paths.
- Egress/TOR measurements, including TOR insert counts and occupancy split by local/remote, miss, opcode, NID, eviction, and writeback classifications.
- CBOX SBo credit acquisition/occupancy and TxR egress allocation/starvation events.

The HA half defines:

- Backup/home tracker cycles and issue hazards.
- Home-agent bypass/direct-to-core/directory optimization behavior.
- Directory lookups and updates.
- HitMe cache lookup/hit/PV-bit records.
- QPI/iMC credit pressure for ingress/read/write queues and memory channels.
- HA request classes split by local/remote reads, writes, and InvItoE traffic.
- HA ring usage, snoop occupancy/responses, snoop response receive classes, OSB and OSB early data return events.
- HA tracker occupancy/cycles and AD/AK/BL TxR egress occupancy/insert/full/not-empty counters.

The event-name family distribution is broad: high-count groups include `UNC_C_TOR_OCCUPANCY` with 21 records, `UNC_C_TOR_INSERTS` with 19, `UNC_H_HITME_HIT` with 13, `UNC_H_HITME_LOOKUP` with 12, and several ring/credit families with 6 to 8 variants each.

## Control Flow and Integration

There is no runtime control flow in this JSON file. Its operational path is data-driven:

1. `tools/perf/pmu-events/Build` depends on the PMU JSON tree and invokes `pmu-events/jevents.py`.
2. `jevents.py` walks architecture/model directories. When it reaches a model leaf such as `arch/x86/haswellx`, it reads every non-metric JSON file, including this file.
3. Each JSON object is parsed into a `JsonEvent`; event code, unit mask, counter mask, filters, package flag, scale unit, and descriptions are converted into generated C initializer strings.
4. The generated `pmu-events.c` exposes opaque `pmu_events_table` data. Mapfile CPU IDs select the `haswellx` table for matching machines.
5. At runtime, perf PMU discovery code in `util/pmu.c` uses `pmu_events_table__find_event()` and related iterators to enrich or create aliases. `perf_pmu__new_alias()` and `update_alias()` copy JSON descriptions, terms, unit scaling, and `perpkg` into `perf_pmu_alias` objects.
6. User-facing commands such as `perf list`, `perf stat -e <alias>`, and Python/listing helpers consume those aliases.

The file therefore integrates with build generation, CPU model selection, PMU alias creation, event parsing, and display/reporting. A malformed event can break generation; a semantically wrong event can compile but make perf program incorrect uncore MSRs.

## State and Persistence Behavior

This file has no mutable state and performs no persistence itself. Its contents become persistent compiled data in generated `pmu-events.c` and then in the perf binary or object outputs.

Runtime state affected by these records is indirect:

- Event aliases are cached in perf PMU alias maps.
- Package-scope aggregation is controlled through the `PerPkg` data.
- `ScaleUnit` affects displayed scale/unit interpretation.
- `Filter` terms are carried into event encoding strings and can program uncore filter fields such as opcode, NID, target ID, and non-coherent qualifiers.

Any change to this JSON requires regeneration/rebuild of perf PMU event tables before the runtime behavior changes.

## Dependencies

Primary dependencies are the perf PMU-event generation and consumption code:

- `pmu-events/jevents.py` reads JSON and emits C tables.
- `pmu-events/pmu-events.h` defines `struct pmu_event`, `struct pmu_events_table`, and lookup/iteration APIs.
- `pmu-events/Build` wires JSON inputs into `pmu-events.c` generation.
- `util/pmu.c` creates and updates runtime aliases from generated event tables.
- `arch/x86/mapfile.csv` maps x86 CPU identifiers to model directories such as `haswellx`.
- Kernel/sysfs PMU devices provide the actual uncore PMU instances and event-source names that must match the generated `Unit`/PMU terms well enough for alias lookup and programming.

The file also depends on Intel Haswellx uncore PMU semantics: event codes, unit masks, counter constraints, TOR/CBOX/HA filter-register behavior, and package-scoped uncore topology.

## Risks and Maintenance Notes

- Counter constraints matter. There are 27 records limited to counter `0`, 8 limited to `0,1,2`, 1 limited to `0,1`, and 362 allowing `0,1,2,3`. Incorrect constraints can cause perf to schedule an event onto an unsupported counter.
- Filtered TOR and LLC aliases rely on `Filter` terms such as `filter_opc=0x182`, `filter_nc=1`, and `filter_tid=0x3e`. If parser syntax or uncore filter field names change, these aliases can silently stop programming the intended MSR filters.
- Some events intentionally omit `EventCode` or `UMask`, but missing fields should be reviewed carefully because accidental omission can generate incomplete encodings or unusable aliases.
- The `UNC_C_LLC_LOOKUP` descriptions warn that umask bit 0 and a state selection must be set or the event counts nothing. Any edits to those masks have high semantic risk.
- `ScaleUnit` is sparse. Only 21 events expose `64Bytes`; related byte-like events without it may report as raw counts, so adding/removing this field changes user-visible interpretation.
- Description text is user-facing and contains some typos or broad copy-paste phrasing. Fixing text is lower risk than changing encodings, but descriptions are still part of perf documentation output and test snapshots.
- CBOX and HA events share this file. Moving HA events to another file would need care because generated topic names and event ordering can affect `perf list` grouping and tests.
- Haswellx uncore behavior is hardware-specific. Copying these events to other x86 model directories without checking Intel uncore PMU documentation risks wrong event codes and filters.

## Test Signals

Useful validation signals after editing this file:

- `jq . sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-cache.json` should parse successfully.
- `jq 'length'` should show the expected event count, or reviewers should account for intentional additions/removals.
- Build generation through `tools/perf/pmu-events/Build` should regenerate `pmu-events.c` without `jevents.py` errors.
- Perf build tests that exercise PMU events, metric parsing, and `perf list` should pass.
- On Haswellx hardware or an environment exposing matching uncore PMUs, `perf list` should show representative aliases such as `LLC_MISSES.DATA_READ`, `UNC_C_TOR_OCCUPANCY.MISS_OPCODE`, and `UNC_H_REQUESTS.READS`.
- Runtime smoke tests should try filtered and counter-constrained events, for example a TOR occupancy counter-0 event and an opcode-filtered LLC/TOR event, to ensure scheduling and filter terms are accepted.
- If descriptions or topics change, compare `perf list --details` output because that path surfaces `BriefDescription`, `PublicDescription`, scale/unit, and package-scope data.
