# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-cache.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006645`: lines 1-5927, `Docs/researches/chunks/subset-b-006645_research.md`
- `subset-b-006646`: lines 5928-12827, `Docs/researches/chunks/subset-b-006646_research.md`
- `subset-b-006647`: lines 12828-13057, `Docs/researches/chunks/subset-b-006647_research.md`

## Chunk Research

### subset-b-006645: lines 1-5927

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

### subset-b-006646: lines 5928-12827

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-cache.json lines 5928-12827

## Scope And Purpose

This chunk is a middle slice of the Cascade Lake Xeon `uncore-cache.json` PMU event table used by Linux `perf`'s `pmu-events` machinery. The full file is a JSON array of event descriptor objects for the `CHA` uncore PMU. This slice starts inside the `UNC_CHA_TxR_VERT_CYCLES_FULL.AD_AG0` object at its final `"Unit": "CHA"` field and continues through the beginning of the deprecated `UNC_H_WRITE_NO_CREDITS.MC1_SMI1` object. Within the slice there are 631 visible `EventName` entries plus that leading partial object.

The active entries in this range describe Cascade Lake CHA mesh, UPI, memory-controller credit, writeback, and cross-snoop events. The larger part of the chunk is a compatibility block of deprecated legacy names, primarily `UNC_C_*` and `UNC_H_*`, each pointing users toward the newer `UNC_CHA_*` spelling while retaining the same low-level event code and umask where applicable. These entries let `perf list` and `perf stat -e <name>` expose both current names and migration aliases for older tooling or user scripts.

## Data Model And Fields

Each complete object is a PMU event descriptor consumed by `tools/perf/pmu-events/jevents.py` and compiled into generated `pmu-events.c`. The schema is data-only; there are no local functions or executable control structures in this JSON file.

Important fields in this chunk:

- `EventName`: canonical or deprecated perf event name, for example `UNC_CHA_UPI_CREDITS_ACQUIRED.AD_REQ` or `UNC_H_TxR_VERT_INSERTS.AD_AG0`.
- `EventCode`: raw hardware event selector, such as `0x90` for vertical TxR occupancy, `0x38` for UPI credits acquired, `0x3B` for UPI credit occupancy, and `0x32` for cross-snoop responses.
- `UMask`: subevent qualifier bits. Many families reuse one event code with different `UMask` values for rings, agents, directions, request sources, responses, or memory-controller channels.
- `Counter`: allowed CHA counter indexes. Most throughput/counting events use `0,1,2,3`; occupancy-style events often restrict to counter `0`.
- `Unit`: always `CHA` in this chunk, binding the event to the cache/home-agent uncore PMU.
- `PerPkg`: set to `1` throughout the visible entries, indicating package-level uncore accounting.
- `Experimental`: present on most entries in this chunk, especially the detailed mesh and deprecated uncore aliases. The visible slice has 592 `Experimental` markers.
- `Deprecated`: present on 532 visible entries, used to preserve old names while steering users to the `UNC_CHA_*` replacements.
- `BriefDescription` and `PublicDescription`: user-facing `perf list` text. For deprecated entries, `BriefDescription` commonly embeds the replacement event name.

No entries in this slice use `Filter` or `ScaleUnit`; filtered derived LLC events and byte-scaling are outside this line range.

## Active Event Families

The chunk begins in the vertical TxR egress section. It includes `UNC_CHA_TxR_VERT_CYCLES_FULL`, `CYCLES_NE`, `INSERTS`, `NACK`, `OCCUPANCY`, and `STARVED` variants. These counters describe Common Mesh Stop vertical egress queue behavior for AD, AK, BL, and IV traffic. The family uses a repeating subevent pattern: AD/AK/BL traffic is split by Agent 0 and Agent 1, while IV is represented as a single subevent. These events are useful for diagnosing vertical-ring pressure, queue fullness, non-empty cycles, insertion rate, NACKs, occupancy, and starvation.

UPI ingress credit events follow. `UNC_CHA_UPI_CREDITS_ACQUIRED.*` counts credit acquisition for VNA/VN0 and AD/BL message classes, including `AD_REQ`, `AD_RSP`, `BL_NCB`, `BL_NCS`, `BL_RSP`, and `BL_WB`. `UNC_CHA_UPI_CREDIT_OCCUPANCY.*` accumulates credit-availability cycles and is explicitly intended to be paired with credits-acquired counts to estimate average credit lifetime. The public descriptions note an external hardware integration detail: the link-select register must choose one UPI link, so users cannot monitor every link from one programmed event.

Vertical ring utilization events cover `UNC_CHA_VERT_RING_AD_IN_USE`, `AK_IN_USE`, `BL_IN_USE`, and `IV_IN_USE`. AD/AK/BL variants split by up/down direction and odd/even ring half; IV has only `UP` and `DN`. The descriptions clarify that these count packets passing or being sunk at the ring stop, excluding packets sent from the stop. They also encode Cascade Lake mesh topology assumptions, where the meaning of "UP" and "DN" depends on which side of the ring the CHA/CBo occupies.

Memory and coherency families in the active section include `UNC_CHA_WB_PUSH_MTOI.{LLC,MEM}`, `UNC_CHA_WRITE_NO_CREDITS.*`, and `UNC_CHA_XSNP_RESP.*`. The write-no-credit family reports lack of iMC write credits for MC0/MC1 and EDC0-EDC3 channels. The cross-snoop response family uses a matrix of request initiator (`ANY`, `CORE`, `EVICT`, `EXT`) and response class (`RSPI_FWDFE`, `RSPI_FWDM`, `RSPS_FWDFE`, `RSPS_FWDM`, `RSP_HITFSE`) under event code `0x32`.

## Deprecated Compatibility Block

After `UNC_CHA_XSNP_RESP.EXT_RSP_HITFSE`, the chunk switches to deprecated aliases. The first group maps older `UNC_C_*` names to newer `UNC_CHA_*` names, including clockticks, fast asserted, LLC lookup, LLC victims, ring source throttle, TOR inserts, and TOR occupancy. Several TOR aliases preserve older queue names such as `IRQ`, `PRQ`, `RRQ`, and `WBQ`, while descriptions point to newer names like `UNC_CHA_TOR_INSERTS.IA`, `IO`, `MISS`, and their hit/miss variants.

Most of the remaining slice maps `UNC_H_*` names to `UNC_CHA_*` names. It includes agent credit acquired/occupancy events, bypass to CHA/iMC, core PMA state/transition events, core snoop events, directory lookup/update, egress ordering, hit-me lookup/hit/miss/update, iMC read/write counts, read/write no-credit events, RxC/RxR retry/reject/insert/occupancy/bypass/starvation families, SF eviction, snoops sent, snoop responses, horizontal and vertical TxR families, ring in-use events, writeback push, and write-no-credit events. The chunk ends in the middle of this alias block, at the opening of `UNC_H_WRITE_NO_CREDITS.MC1_SMI1`.

The deprecated entries are not dead data. They intentionally remain visible so perf can warn users through naming and descriptions while still resolving legacy event names to raw CHA encodings. Removing or changing them can break existing scripts that still use `UNC_C_*` or `UNC_H_*`.

## Control Flow And Generation Path

At build time, `tools/perf/pmu-events/Build` invokes `pmu-events/jevents.py` over `pmu-events/arch`. The script reads JSON event files like this one, normalizes descriptors into event table records, and generates `pmu-events.c`. Runtime perf code then uses the generated tables through `pmu-events/pmu-events.h` and PMU lookup helpers in `util/pmu.c`.

The control flow for this chunk is therefore declarative:

1. `arch/x86/mapfile.csv` maps Cascade Lake Xeon model identifiers to the `cascadelakex` event directory.
2. `jevents.py` parses this JSON array and stores fields such as event name, description, event code, umask, counter mask, per-package flag, experimental flag, and deprecation flag.
3. Perf's event listing and parsing paths expose the generated records for the matching CPU model and PMU unit.
4. When a user selects an event, perf programs the matching CHA event code and umask on valid uncore counters.

There is no per-event runtime state in this file. The state exists in the generated C tables and, later, in perf's PMU configuration for a measurement session.

## State And Persistence Behavior

The source file is persistent repository data used to generate a static event catalog. Its entries should be treated as ABI-like metadata for perf users because event names, event codes, umasks, deprecation markers, and descriptions affect command-line compatibility and generated output.

State-sensitive behavior implied by the data:

- Occupancy events, especially `UNC_CHA_UPI_CREDIT_OCCUPANCY.*` and `UNC_CHA_TxR_VERT_OCCUPANCY.*`, accumulate cycles or queue occupancy and are interpreted in relation to paired allocation/acquisition events.
- The `Counter` field constrains scheduling. Entries with only counter `0` can be harder to multiplex than entries allowing `0,1,2,3`.
- `PerPkg` makes these package-scope uncore events; users should not interpret them as per-core counters.
- The deprecated aliases persist alongside current names and should continue to generate equivalent hardware encodings unless intentionally removed by a compatibility decision.

## Dependencies And Integration Points

The direct integration point is Linux perf's PMU event generator. `jevents.py` is the schema consumer, `pmu-events/Build` wires generation into the perf build, and `util/pmu.c` consumes the generated tables for event discovery and parsing. `builtin-list.c` prints fields such as `EventName` and `Deprecated` in JSON output, so metadata quality directly affects `perf list --json` consumers.

The model integration is through `pmu-events/arch/x86/mapfile.csv`, where Cascade Lake Xeon family/model patterns select `cascadelakex`. The hardware integration is Intel CHA uncore PMU programming: `Unit: CHA`, `EventCode`, `UMask`, and `Counter` together describe what perf can program on that PMU. UPI credit events additionally depend on external link-selection programming described by the event text.

This source tree is under `sources/distributed-fs/ceph-client`, but this particular file is from the vendored Linux `tools/perf` subtree. It does not integrate with Ceph client logic directly.

## Risks And Edge Cases

The range boundaries are not object-aligned. Line 5928 is only the `Unit` field of `UNC_CHA_TxR_VERT_CYCLES_FULL.AD_AG0`, and line 12827 begins another deprecated object. Merge/reconciliation should use the full file context when producing a final per-file report.

The event descriptions contain hardware semantics and several subtle constraints. The vertical ring direction descriptions depend on mesh side and odd/even ring selection. The UPI credit descriptions state that only one link can be monitored at a time through link select. Losing those details would make the generated perf help less accurate.

Many deprecated entries have only a brief replacement pointer and no `PublicDescription`. That is expected for aliases, but tools consuming descriptions should tolerate sparse metadata. Some deprecated descriptions say only "This event is deprecated." without a replacement, so automated migration tooling cannot rely on every legacy entry naming a target.

Counter restrictions matter. If an occupancy alias or active occupancy event is accidentally changed from `Counter: "0"` to all counters, or vice versa, perf scheduling and measurement validity can change. Likewise, mistakes in shared event-code/umask matrices can silently remap a user-visible name to the wrong hardware subevent.

Most active entries in this chunk are marked experimental. Metrics or dashboards built on them should expect less stability than basic architectural counters. The deprecation block also makes duplicate hardware encodings visible under multiple names, so documentation and tests need to distinguish intentional aliases from accidental duplicates.

## Test Signals

Useful validation signals are mostly generator and perf-tool tests rather than unit tests local to this JSON file:

- The full `uncore-cache.json` must remain valid JSON; `jq 'length'` currently parses it as 1203 event objects.
- `tools/perf/pmu-events/jevents.py` generation should succeed for the `cascadelakex` model without schema errors.
- Perf PMU event tests in `tools/perf/tests/pmu-events.c` provide generated-table sanity coverage.
- `perf list` on a matching Cascade Lake Xeon system should expose the active `UNC_CHA_*` names and mark deprecated `UNC_C_*`/`UNC_H_*` aliases appropriately.
- `perf list --json` should preserve fields used by external tooling, especially `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `Experimental`, and `Deprecated`.
- Hardware smoke tests, where available, can compare paired counters such as UPI credits acquired versus UPI credit occupancy, TxR inserts versus occupancy/starvation, and write-no-credit events under memory pressure.

### subset-b-006647: lines 12828-13057

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-cache.json lines 12828-13057

## Scope

This chunk covers the final entries in the Cascade Lake Xeon `uncore-cache.json` PMU event table. It is data, not executable code: JSON objects that the perf `pmu-events` build pipeline converts into generated C event tables. The requested line range starts inside the first event object, so the first logical entry is continued from the preceding chunk: `UNC_H_WRITE_NO_CREDITS.MC1_SMI1` has its `BriefDescription` on line 12827 and the rest of the object in this slice. The chunk then contains the complete tail of the file, ending with the closing JSON array on line 13057.

The slice describes deprecated `UNC_H_*` uncore cache/home-agent aliases. Each entry points users toward the newer `UNC_CHA_*` event spelling while preserving the old alias in the model event database.

## Purpose

The purpose of these entries is compatibility for older Cascade Lake Xeon uncore event names. They allow perf users, scripts, and metric definitions that still reference `UNC_H_WRITE_NO_CREDITS.*` or `UNC_H_XSNP_RESP.*` to continue resolving a symbolic event, while marking the name deprecated and documenting the replacement.

The first event in the chunk maps the old home-agent write-credit alias `UNC_H_WRITE_NO_CREDITS.MC1_SMI1` to `UNC_CHA_WRITE_NO_CREDITS.MC1_SMI1`. The remaining twenty events map old external snoop response aliases under `UNC_H_XSNP_RESP` to the equivalent `UNC_CHA_XSNP_RESP` names.

## Important Data Fields

Every event object in this slice uses the perf PMU JSON schema fields consumed by `tools/perf/pmu-events/jevents.py`:

- `EventName`: the user-visible symbolic event name. `jevents.py` lowercases it when generating the compiled table, but perf matching still presents the original semantic name to users through the event database/listing path.
- `BriefDescription`: the only description field present for these entries. It states that the event is deprecated and names the replacement event.
- `Deprecated`: set to `"1"` for all entries in the chunk. This becomes the `deprecated` boolean in `struct pmu_event`.
- `Experimental`: set to `"1"` for all entries, indicating the event definition should be treated as experimental metadata.
- `EventCode` and `UMask`: the hardware selector fields that form the encoded perf event. `UNC_H_WRITE_NO_CREDITS.MC1_SMI1` uses event code `0x5A`, while every `UNC_H_XSNP_RESP.*` alias uses event code `0x32` with variant-specific unit masks.
- `Counter`: `"0,1,2,3"` for all entries, restricting them to the four CHA uncore counters.
- `Unit`: `"CHA"` for all entries. `jevents.py` maps this unit string to the target uncore PMU name for the generated event entry.
- `PerPkg`: `"1"` for all entries, so the generated `pmu_event` records are package-scoped uncore events rather than per-core CPU events.

The `UNC_H_XSNP_RESP` entries are organized by requester/source class and response class:

- `ANY_*` masks: `0xe4`, `0xf0`, `0xe2`, `0xe8`, and `0xe1`.
- `CORE_*` masks: `0x44`, `0x50`, `0x42`, `0x48`, and `0x41`.
- `EVICT_*` masks: `0x84`, `0x90`, `0x82`, `0x88`, and `0x81`.
- `EXT_*` masks: `0x24`, `0x30`, `0x22`, `0x28`, and `0x21`.

Within each group, the suffixes are `RSPI_FWDFE`, `RSPI_FWDM`, `RSPS_FWDFE`, `RSPS_FWDM`, and `RSP_HITFSE`. The repeated mask pattern suggests the high bits select the requester/source class and the low bits select the snoop-response condition.

## APIs, Types, And Generated Representation

This JSON is consumed by the perf PMU events generator rather than by normal C APIs directly. `jevents.py` reads each JSON object, constructs an internal event representation, and emits generated C into `pmu-events/pmu-events.c`. The generated data is exposed through `pmu-events/pmu-events.h`, especially:

- `struct pmu_event`, whose fields include `name`, `event`, `desc`, `pmu`, `unit`, `perpkg`, and `deprecated`.
- `pmu_events_table__for_each_event()`, which iterates events for a matched table and PMU.
- `pmu_events_table__find_event()`, which resolves a named event against a table and PMU.

For these records, `EventCode` and `UMask` become the event encoding string that perf uses to populate `perf_event_attr.config`. `BriefDescription` becomes `desc`; `Unit` influences the generated `pmu` binding; `PerPkg` and `Deprecated` become booleans. There are no `PublicDescription`, `Filter`, `ScaleUnit`, metric expression, or threshold fields in this chunk.

## Control Flow

There is no runtime control flow in the JSON file itself. The effective flow is:

1. During the perf build, `tools/perf/pmu-events/Build` invokes `jevents.py` for the selected architecture.
2. `jevents.py` recursively traverses `tools/perf/pmu-events/arch/x86`, reads model JSON files such as this `cascadelakex/uncore-cache.json`, and validates/transforms each event object.
3. The generator emits compact generated event tables into `pmu-events.c`.
4. The generated object is built into `libpmu-events.a` and then linked into perf.
5. At runtime, perf identifies the CPU model through `arch/x86/mapfile.csv`, selects the Cascade Lake Xeon event table, and exposes matching CHA events as symbolic aliases.
6. Commands such as `perf list`, `perf stat -e <event>`, and metric expansion can find these old aliases, while list-style output can also show the deprecated flag.

Because this chunk is the tail of the JSON array, syntax at the final object matters: the last `UNC_H_XSNP_RESP.EXT_RSP_HITFSE` object has no trailing comma and is followed by the closing `]`.

## State And Persistence Behavior

The only persistent state is the checked-in event metadata and the generated `pmu-events.c` produced from it at build time. The JSON does not create mutable program state, open files, or store runtime data.

At runtime, the event state lives in perf's generated event tables and in any `perf_event_attr` instances created from a selected alias. For these events, the relevant hardware state is package-level CHA uncore counter configuration. The `PerPkg` flag is important because perf should aggregate/count the event at package scope, not as a normal per-thread or per-core event.

The deprecated aliases are persistent compatibility surface. Removing or renaming them would not change the newer `UNC_CHA_*` events, but it would break older command lines and automation that still use the `UNC_H_*` names.

## Dependencies And Integration Points

This chunk depends on the perf PMU event infrastructure:

- `tools/perf/pmu-events/README` defines the JSON-directory, mapfile, generation, and runtime alias model.
- `tools/perf/pmu-events/jevents.py` parses fields such as `EventName`, `BriefDescription`, `Unit`, `PerPkg`, and `Deprecated`.
- `tools/perf/pmu-events/pmu-events.h` defines the generated event/metric table interfaces and `struct pmu_event`.
- `tools/perf/builtin-list.c` can print JSON/list output including `EventName`, `Deprecated`, and `BriefDescription`.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` maps x86 CPU IDs to model directories such as `cascadelakex`.
- The Linux uncore PMU driver and sysfs PMU descriptions must expose a compatible CHA PMU so the generated event encodings can be scheduled on real hardware.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file belongs to the vendored Linux perf tooling tree. It has no direct CephFS client control flow or distributed file-system behavior.

## Risks And Edge Cases

The line range begins in the middle of `UNC_H_WRITE_NO_CREDITS.MC1_SMI1`, so chunk-level review must avoid treating lines 12828-12835 as a standalone JSON object. The full file is valid because the opening brace and `BriefDescription` are immediately before the requested range.

Alias accuracy is the main semantic risk. The `BriefDescription` replacement names must match real `UNC_CHA_*` definitions elsewhere in the same model data. If an alias keeps the old name but carries the wrong `EventCode` or `UMask`, perf will successfully parse it but program a different CHA counter than users expect.

Deprecation handling is also a compatibility risk. These events should remain discoverable for old workflows, but UI and documentation should steer new users to `UNC_CHA_*`. Dropping the `Deprecated` flag would make stale names look current; deleting the aliases would break older command lines.

The event scope is package-level CHA uncore, so users may get confusing results if they compare these counters directly with per-core events or run on hardware whose uncore PMUs are unavailable, disabled, renamed, or permission-restricted.

The chunk's final `]` makes it sensitive to JSON syntax churn. A missing comma before this slice, an accidental trailing comma at the final event, or malformed quoting in any description would break `jevents.py` generation for the whole model table.

## Test Signals

Useful validation signals for this chunk include:

- Running the PMU event generation path for x86 and confirming `pmu-events.c` is produced without JSON parse errors.
- Building perf with jevents enabled so the generated event tables compile into `libpmu-events.a`.
- Running the perf PMU event tests, especially `tools/perf/tests/pmu-events.c`, to catch generated-table regressions.
- On Cascade Lake Xeon hardware, checking `perf list --details` or JSON list output for deprecated `UNC_H_WRITE_NO_CREDITS.MC1_SMI1` and representative `UNC_H_XSNP_RESP.*` aliases.
- Verifying that `perf stat -e` accepts both old `UNC_H_*` aliases and the replacement `UNC_CHA_*` names where the CHA uncore PMU is available.
- Spot-checking generated encodings for the `0x5A/0x2` write-credit event and several `0x32` XSNP response masks from the `ANY`, `CORE`, `EVICT`, and `EXT` groups.

## Cross-Chunk Notes

This document intentionally covers only lines 12828-13057. The previous chunk is needed for the full first object's `BriefDescription`, and the merge lane should combine adjacent chunks before producing a whole-file report for `uncore-cache.json`.
