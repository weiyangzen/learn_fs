# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-cache.json lines 1-5927

## Scope

This chunk covers the first 5,927 lines of the Cascade Lake X `uncore-cache.json` PMU event table used by the vendored Linux `tools/perf` tree. The full file is a JSON array of hardware performance monitoring event objects; this range starts at the array open and ends in the middle of the `UNC_CHA_TxR_VERT_CYCLES_FULL.AD_AG0` object, just before its `"Unit": "CHA"` field on the next line. The final per-file reconciliation must combine this with later chunks before treating the source as complete JSON.

The range contains 551 `EventName` entries, all for the Cascade Lake X uncore cache/home-agent PMU. Most entries target the `CHA` unit and expose Common Mesh Stop, LLC, TOR, snoop, ring, ingress, egress, credit, occupancy, retry, rejection, and starvation counters. The opening entries also define derived LLC miss/reference aliases for MMIO, uncacheable reads, and streaming stores.

## Purpose

The file is declarative data, not executable Ceph filesystem logic. Its purpose is to teach `perf` which named events are available on Cascade Lake X uncore cache PMUs and how to encode each event for the kernel PMU interface. During the `tools/perf` build, `pmu-events/Build` includes `pmu-events/arch/**/*.json` as inputs, optionally copies them into the output tree, and runs `pmu-events/jevents.py` to generate `pmu-events.c`. At runtime, perf uses the generated tables to resolve user-facing event names into PMU config strings.

The event objects preserve Intel PMU metadata: `EventCode`, `UMask`, `Filter`, `Counter`, `Unit`, package aggregation hints, short and long descriptions, and flags such as `Experimental` and `Deprecated`. For this chunk the data primarily describes CHA-level mesh/cache telemetry rather than derived high-level metrics; no `MetricName` or `MetricExpr` entries appear in the range.

## Important Data Contract

Each event object follows the perf PMU JSON schema consumed by `jevents.py`. The important fields in this chunk are:

- `EventName`: the public perf event name, lowercased by `jevents.py` when stored in generated tables.
- `EventCode`: the base hardware event select value. In this range codes span low CHA events such as `0x11`, `0x13`, `0x17`, `0x18`, `0x19`, cache/TOR codes such as `0x33` through `0x37`, ring and Rx/Tx codes such as `0x50` through `0x64`, credit/egress codes such as `0x80` through `0xA9`, and mesh/IMC-related codes through `0xD6`.
- `UMask`: the subevent mask appended by `jevents.py` as `umask=<value>` when non-zero.
- `Filter`: optional raw filter text appended to the generated perf event string. The beginning of the chunk uses `config1=...` filters for derived LLC/TOR request classes and other qualified CHA request classes.
- `Counter`: usually `"0,1,2,3"`, describing the uncore counters that can host the event.
- `Unit`: mostly `"CHA"`, mapped by `jevents.py` to the `uncore_cha` PMU name.
- `PerPkg`: `"1"` for package-level uncore aggregation.
- `ScaleUnit`: present only for the two streaming-store aliases, where the count is scaled as `64Bytes`.
- `Experimental`: present on the majority of the range, marking many low-level CHA mesh and credit events as experimental.
- `Deprecated`: present on a smaller set, signaling events that should remain visible for compatibility but are not preferred.
- `BriefDescription` and `PublicDescription`: short and detailed user-facing documentation copied into generated perf tables after description cleanup.

`jevents.py` constructs the final event encoding roughly as `event=<EventCode>,umask=<UMask>,<Filter>`, with optional conversions for other supported JSON fields. For this file, `Unit: "CHA"` is the integration key that routes names to the uncore CHA PMU rather than a core PMU.

## Event Families in This Chunk

The first five entries define derived LLC aliases: `LLC_MISSES.MMIO_READ`, `LLC_MISSES.MMIO_WRITE`, `LLC_MISSES.UNCACHEABLE`, `LLC_REFERENCES.STREAMING_FULL`, and `LLC_REFERENCES.STREAMING_PARTIAL`. They are derived from `unc_cha_tor_inserts.ia_miss`, use event code `0x35` and umask `0x21`, and distinguish request classes with `config1` filters. The streaming-store entries add `ScaleUnit: "64Bytes"`.

The next groups cover Common Mesh Stop agent credits and occupancy: `UNC_CHA_AG0_*` and `UNC_CHA_AG1_*` families for AD and BL credits acquired or occupied, with six transgress subevents each. These events expose resource-pressure information for mesh agents and are flagged experimental.

The middle of the chunk enumerates a broad CHA cache/coherency surface: bypass to CHA/IMC, CHA and CMS clockticks, core PMA and snoop events, directory lookup/update, egress ordering, fast asserted, HITME hit/lookup/miss/update, horizontal ring in-use counters, IMC read/write counts, IODC allocation/deallocation, LLC lookup and victim events, miscellaneous CHA events, PMM memory-mode set conflicts, read-no-credit events, requests, ring bounces, ring sink/source starvation, SF eviction, snoops sent, and local/non-local snoop responses.

The `UNC_CHA_RxC_*` and `UNC_CHA_RxR_*` families occupy a large part of the range. They describe ingress-side inserts, queue rejection and retry counters for IPQ, IRQ, ISMQ, PRQ, request queues, read-request queues, writeback queues, other queues, occupancy, bypass, busy-starved, credit-starved, and related receiver ring activity. These entries often repeat the same base event code with subevent `UMask` values for AD, AK, BL, IV, SNP, or queue lane variants.

The `UNC_CHA_TOR_INSERTS` and `UNC_CHA_TOR_OCCUPANCY` groups are the densest cache-miss/request tracking families in the chunk. They differentiate demand reads, prefetches, writes, IO, IA misses, LLC misses, local and remote requests, and filtered variants. These are the source for several derived aliases at the start of the file and are central to uncore cache/TOR analysis on Cascade Lake X.

The end of the chunk enters transmit-ring egress telemetry. It includes `UNC_CHA_TxR_HORZ_ADS_USED`, horizontal bypass, full/not-empty cycles, inserts, NACKs, occupancy, and starvation, followed by vertical ADS-used and bypass events. The final object begun in this chunk is `UNC_CHA_TxR_VERT_CYCLES_FULL.AD_AG0`; its object is completed after line 5927.

## Control Flow

There is no local runtime control flow in the JSON file. The relevant control flow is the build and lookup path around it:

1. `tools/perf/pmu-events/Build` discovers JSON and CSV inputs under `pmu-events/arch`, including `arch/x86/cascadelakex/uncore-cache.json`.
2. The build may copy source JSON files into the output tree when an external `OUTPUT` directory is used.
3. `jevents.py` reads the JSON objects, converts each event object into an internal event representation, and emits generated C tables in `pmu-events.c`.
4. `jevents.py` maps `Unit: "CHA"` to the `uncore_cha` PMU name, lowercases `EventName`, canonicalizes numeric values, appends `UMask` and `Filter` fields to the event string, and carries descriptions, `PerPkg`, units, deprecated state, and metric fields when present.
5. Perf command paths later use the generated event map selected by x86 `mapfile.csv`. The mapfile associates `GenuineIntel-6-55-[56789ABCDEF]` with the `cascadelakex` model directory, so these events are selected for matching Cascade Lake X-family CPUs.

For users, the observable flow is name resolution: a request for a named event such as a TOR insert, RxC rejection, or TxR bypass event resolves to an uncore CHA PMU event encoding with the proper event select, umask, and optional `config1` filter.

## State and Persistence Behavior

The JSON source is static repository data. It has no mutable in-process state, no persistence side effects, and no direct I/O behavior beyond being read by the perf build. Its persistent effect is the generated `pmu-events.c` table that becomes part of the perf binary or library build output.

At runtime, `PerPkg: "1"` tells perf that these uncore events are package-scoped. Counting state lives in kernel PMU counters and perf event file descriptors, not in this JSON. The `Counter` field constrains counter assignment, while `Filter` values influence hardware request classification through PMU config fields.

Because the chunk boundary cuts through an event object, this line range alone is not a standalone JSON document. The full source file is the persisted authoritative data; chunk-level research should not be used to validate syntax independently.

## Dependencies and Integration Points

The immediate dependencies are the perf PMU event tooling:

- `tools/perf/pmu-events/Build` for discovering JSON inputs, generating extra metric JSON, running `metric_test.py`, checking the empty PMU event output, and invoking `jevents.py`.
- `tools/perf/pmu-events/jevents.py` for parsing the event schema and emitting generated C.
- `tools/perf/pmu-events/metric.py` for metric parsing, though this chunk itself does not define metrics.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` for connecting Cascade Lake X CPUID patterns to the `cascadelakex` directory.
- Perf PMU lookup code under `tools/perf/util/pmu*` and related generated `pmu-events` headers for consuming the emitted tables.

The hardware integration point is Intel Cascade Lake X uncore CHA PMU support exposed through the Linux perf_event subsystem. The `Unit` and event encoding fields must match kernel PMU naming and hardware programming semantics for `uncore_cha`.

Although this repository is named as a Ceph client source tree, this file is a vendored Linux tools/perf data asset. It does not integrate with Ceph distributed filesystem code paths directly.

## Risks and Edge Cases

The largest risk is silent data drift. If Intel event definitions, `EventCode`, `UMask`, `config1` filter encodings, package aggregation, or deprecation/experimental flags are wrong, perf can report plausible but incorrect hardware counts.

Schema drift is also important. `jevents.py` has explicit handling for known JSON keys; misspelled or unsupported keys may be dropped or fail generation depending on parser behavior. Since the event objects are repetitive, a copy/paste error in one subevent can be hard to notice without generated-table or hardware validation.

`Filter` strings are raw fragments appended to event encodings. Bad `config1` values, case differences, or malformed filter syntax would propagate directly into generated event descriptions and can break event opening or select the wrong transaction class.

The many experimental entries are low-level implementation counters. Their semantics may be undocumented, platform-specific, or unstable across related Intel server parts. Consumers should avoid treating them as stable architectural events.

Package-level CHA counting can surprise users on multi-socket systems. `PerPkg` aggregation and one event instance per uncore PMU can produce counts that need explicit socket/package interpretation rather than per-thread interpretation.

Some descriptions appear internally inconsistent or inherited from related counters. For example, the vertical/full-cycle wording at the end of the chunk says "Queue Is Full" while the public description text says "was Not Full"; this kind of textual mismatch is a documentation risk even if the event encoding is correct.

The chunk starts at the file open but ends before completing the final object in scope. Any automated checker run against only this range would fail JSON parsing; validation must use the full source file.

## Test Signals

Useful validation signals for this chunk include:

- Build `tools/perf` with `JEVENTS_ARCH=x86` or full PMU event generation and confirm `pmu-events.c` is generated without JSON/schema errors.
- Run the `pmu-events/metric_test.py` build target even though this chunk has no metrics, because the same build path validates generated PMU assets globally.
- Inspect generated `pmu-events.c` for representative events from each family, verifying lowercased names, `uncore_cha` PMU mapping, `event=...`, `umask=...`, `config1=...`, `perpkg`, `deprecated`, and `ScaleUnit` output where expected.
- On a matching Cascade Lake X system, run `perf list` and confirm representative names appear under uncore CHA events, including `LLC_MISSES.MMIO_READ`, `UNC_CHA_TOR_INSERTS.*`, `UNC_CHA_RxC_*`, and `UNC_CHA_TxR_*`.
- On hardware, try opening representative non-filtered and filtered events with `perf stat -e` to catch invalid event encodings, invalid `config1` filters, counter constraints, and package aggregation surprises.
- Compare event codes, umasks, and descriptions against Intel's Cascade Lake X uncore PMU reference or upstream Linux perf PMU event data when updating this file.
- Use JSON formatting validation on the complete `uncore-cache.json`, not this chunk alone.

## Cross-Chunk Notes

This document covers only lines 1-5927. The final event object in scope continues after the boundary, and the source file continues to line 13057 with the remaining Cascade Lake X uncore cache events. The merge lane should combine all chunks for this source before producing a per-file report, especially for complete syntax validation, tail event families, and any closing-array behavior.
