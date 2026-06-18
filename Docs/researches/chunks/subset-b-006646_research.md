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
