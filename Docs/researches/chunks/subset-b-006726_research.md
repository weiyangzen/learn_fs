# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-interconnect.json lines 1-6272

This chunk covers the opening 6,272 lines of the Skylake Xeon `uncore-interconnect.json` PMU event table. It starts at the JSON array opener and contains 597 complete visible event records through `UNC_M3UPI_RING_BOUNCES_HORZ.AD`. The final requested line, 6272, is inside the next event object after its `EventCode`; that object's `EventName` and remaining fields begin after this chunk. The full source file has 13,758 lines, so this is only the first portion of a larger uncore interconnect event table.

## Purpose

This file is static perf PMU metadata, not executable Ceph filesystem logic. Its purpose is to describe Intel Skylake X uncore interconnect hardware events so the Linux `perf` build can generate model-specific event lookup tables. The generated tables let users and metrics refer to symbolic event aliases such as `UNC_I_TRANSACTIONS.READS`, `UNC_M2M_IMC_READS.ALL`, and `UNC_M3UPI_CLOCKTICKS` instead of manually encoding raw event select, umask, counter, and unit values.

The chunk covers three uncore units:

- `IRP`: 76 complete events for inbound request port traffic, coherent operations, P2P traffic, snoop responses, FAF/P2P queue occupancy, and IRP egress stalls.
- `M2M`: 433 complete events for Mesh-to-Memory credit accounting, direct-to-core/direct-to-UPI paths, directory lookups/updates, iMC reads/writes, prefetch CAMs, trackers, CMS ingress/egress queues, transgress credits, ring usage, ring bounces, starvation, NACKs, bypasses, and anti-deadlock slot usage.
- `M3UPI`: 88 complete events for the beginning of the M3/UPI interconnect section, including CMS agent credits, CHA/M2 credit-empty conditions, clockticks, D2C/D2U sends, ordering stalls, FaST distress signals, horizontal ring use, M2 BL credit-empty masks, multi-slot flit receives, and the first horizontal ring-bounce event.

## Schema And API Surface

Each complete object follows the perf PMU event JSON schema consumed by `tools/perf/pmu-events/jevents.py`:

- `EventName`: stable user-facing alias. It encodes the hardware block and subtype, for example `UNC_M2M_TxR_VERT_OCCUPANCY.BL_AG1`.
- `EventCode`: raw event select value programmed for the unit's PMU. Some clock events, such as `UNC_M2M_CLOCKTICKS`, omit it when the event is special-cased by the PMU description.
- `UMask`: event subtype mask. Many event families share one `EventCode` and distinguish variants only by `UMask`.
- `Counter`: allowed hardware counter indexes. IRP events mostly use `0,1`; M2M mostly uses `0,1,2,3`; M3UPI mostly uses `0,1,2`, with narrower exceptions such as some AG1 BL occupancy entries using counter `0`.
- `Unit`: routes the event to the generated uncore PMU namespace. In this chunk the units are `IRP`, `M2M`, and `M3UPI`.
- `PerPkg`: all complete events in this chunk are package-scoped uncore events.
- `BriefDescription` and optional `PublicDescription`: user-visible `perf list` documentation.
- `Experimental` and `Deprecated`: metadata flags. Most low-level ring/credit events are marked experimental; the older `UNC_M2M_RPQ_CYCLES_NO_SPEC_CREDITS.CHN*` aliases are marked deprecated and point users toward `UNC_M2M_RPQ_CYCLES_SPEC_CREDITS.CHN*`.

The generated C API surface is defined by `tools/perf/pmu-events/pmu-events.h`, especially `struct pmu_event`, `struct pmu_events_table`, `pmu_events_table__for_each_event()`, `pmu_events_table__find_event()`, `perf_pmu__find_events_table()`, and `find_core_events_table()`. This JSON is an input to those generated tables rather than a runtime parser input.

## Event Families

The `IRP` section defines inbound request port measurements:

- Cache/queue occupancy and clocks: `UNC_I_CACHE_TOTAL_OCCUPANCY.*`, `UNC_I_CLOCKTICKS`, FAF/P2P inserts and occupancy, and outbound request occupancy.
- Coherency and transaction classification: `UNC_I_COHERENT_OPS.*` distinguishes CLFLUSH, CRd, DRd, PCIRdCur, PCITOM, RFO, WbMtoI, and related operations; `UNC_I_TRANSACTIONS.*` separates reads, write prefetches, read prefetches, writes, atomics, and other transactions.
- P2P, snoop, and misc diagnostics: `UNC_I_P2P_TRANSACTIONS.*`, `UNC_I_SNOOP_RESP.*`, `UNC_I_MISC0.*`, and `UNC_I_MISC1.*` expose local/remote matches, MESI response states, fast-path behavior, secondary-transfer state, and lost-forward conditions.
- IRP transmit-side queues and stalls: `UNC_I_TxC_*`, `UNC_I_TxR2_*`, and `UNC_I_TxS_*` cover BL/AK egress queues, credit stalls, and switch-bound request/data insertion.

The `M2M` section is the largest part of this chunk:

- Agent/transgress credit families repeat across Agent 0/1, AD/BL, acquired/occupancy, and transgress indexes 0-5.
- Directory and bypass events cover M2M-to-iMC bypass, direct-to-core/direct-to-UPI operation, directory hit/miss states, multi-socket directory lookup states, and directory state transitions such as `I2S`, `S2A`, and `A2I`.
- iMC, prefetch, and tracker events count reads/writes, priority classes, prefetch CAM inserts/promotions/occupancy/full cycles, RPQ credit cycles by channel, and tracker cycles/inserts/occupancy by channel.
- CMS receive/transmit queues are split into `RxC`, `RxR`, `TxC`, `TxR_HORZ`, and `TxR_VERT` families. They expose inserts, occupancy, full/not-empty cycles, bypass, starvation, credit-starved, no-credit, NACK, and anti-deadlock slot usage.
- Ring events classify AD/AK/BL/IV usage across vertical and horizontal directions, left/right sides, even/odd rings, source throttling, sink starvation, ring bounces, and FaST distress assertions.

The `M3UPI` section begins a similar matrix for M3/UPI-facing uncore traffic:

- CMS agent credit events mirror the M2M pattern for AD and BL credits, with counters adjusted for the M3UPI PMU.
- Credit-empty and direct-send families include `UNC_M3UPI_CHA_AD_CREDITS_EMPTY.*`, `UNC_M3UPI_M2_BL_CREDITS_EMPTY.*`, `UNC_M3UPI_D2C_SENT`, and `UNC_M3UPI_D2U_SENT`.
- The chunk includes horizontal ring-in-use events for AD, AK, BL, and IV rings, multi-slot flit receive masks, and starts the ring-bounce family at `UNC_M3UPI_RING_BOUNCES_HORZ.AD`.

## Control Flow

The effective control flow is data-driven:

1. `tools/perf/pmu-events/Build` includes PMU JSON files and invokes `pmu-events/jevents.py` to generate `$(OUTPUT)pmu-events/pmu-events.c`.
2. `jevents.py` traverses model directories such as `arch/x86/skylakex`, reads JSON event objects, normalizes fields, maps `Unit` values to PMU names, lowercases event aliases internally, and emits compact generated event tables.
3. `tools/perf/pmu-events/arch/x86/mapfile.csv` maps Intel family/model patterns to the `skylakex` model directory; in this tree `GenuineIntel-6-55-[01234]` selects `skylakex`.
4. Runtime perf code finds the host PMU event table through generated lookup functions and exposes aliases through `perf list`, `perf stat -e`, metric expansion, and JSON/list output.
5. When a user selects one of these aliases, perf resolves `EventName` plus optional unit context to the encoded `EventCode`, `UMask`, `Counter`, `Unit`, package-scope flag, and descriptions generated from this JSON.

There is no imperative control flow in the JSON itself. Ordering still matters for generated output stability, diff review, and chunk reconciliation.

## State And Persistence

This source file has no mutable runtime state and no direct persistence behavior. Its persistent contract is the checked-in mapping from symbolic event names to hardware encodings and descriptions. During a perf build, that metadata is transformed into generated `pmu-events.c`; after compilation it becomes read-only data linked into perf. Runtime counter state is owned by the kernel PMU drivers and active perf sessions, not by this JSON file.

Name, code, mask, unit, and deprecation changes are persistent compatibility changes. They can alter `perf list` output, break scripts that request specific event aliases, change metric formulas that reference those aliases, or program different uncore counters on Skylake X systems.

## Dependencies And Integration Points

- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/Build` discovers PMU JSON inputs and runs `jevents.py`.
- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/jevents.py` parses schema fields such as `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `BriefDescription`, `PublicDescription`, `PerPkg`, `Experimental`, and `Deprecated`.
- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/pmu-events.h` defines generated table interfaces and `struct pmu_event`.
- `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/mapfile.csv` maps x86 CPUID patterns to the `skylakex` event directory.
- `sources/distributed-fs/ceph-client/tools/perf/tests/pmu-events.c` validates generated event tables and alias behavior.
- Perf PMU listing and event parsing code consumes the generated aliases, while metric code can depend on event-name stability even though this file itself defines events rather than formulas.

## Risks And Edge Cases

The chunk boundary is mid-object. Lines 6269-6272 begin the `UNC_M3UPI_RING_BOUNCES_HORZ.AK` object but stop before its `EventName`, `Experimental`, `PerPkg`, `PublicDescription`, `UMask`, `Unit`, and closing brace. This chunk is therefore not independently parseable as JSON; only the complete source file is.

The event matrix is highly repetitive, so copy/paste drift is a real maintenance risk. Similar names differ only by agent, direction, channel, ring type, or transgress bit, and a wrong `UMask` or `Counter` can silently produce a valid generated table with incorrect hardware behavior.

Description quality is uneven. Several descriptions contain typos or label drift, such as "PCIDCAHin5t", "prefect queue", `QPI` wording in a UPI-era file, and some `CYCLES_FULL` descriptions that say "Not Full" in nearby M2M vertical egress text. Consumers should treat `EventName`, `EventCode`, `UMask`, `Counter`, and Intel hardware documentation as the authoritative behavioral mapping when descriptions conflict.

Deprecated entries must remain usable until intentionally removed. The `UNC_M2M_RPQ_CYCLES_NO_SPEC_CREDITS.CHN*` records are marked deprecated but still carry encodings; removing or renaming them can break existing scripts.

Many entries are marked `Experimental`, especially deep ring, credit, and starvation diagnostics. Tooling should preserve that flag so users understand these aliases may be less stable or less validated than standard events.

## Test Signals

Useful validation signals for this chunk and its final merged file include:

- Strictly parse the complete file with a JSON parser, for example `python3 -m json.tool sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-interconnect.json`.
- Regenerate perf PMU events for x86/skylakex and confirm `pmu-events.c` generation completes without schema, numeric conversion, duplicate-name, or unit-mapping errors.
- Inspect generated entries for representative events from each covered unit: `UNC_I_TRANSACTIONS.READS`, `UNC_I_SNOOP_RESP.ALL_HIT`, `UNC_M2M_DIRECTORY_LOOKUP.STATE_A`, `UNC_M2M_IMC_WRITES.PARTIAL`, `UNC_M2M_TxR_VERT_OCCUPANCY.IV`, `UNC_M2M_VERT_RING_AD_IN_USE.UP_EVEN`, `UNC_M3UPI_CLOCKTICKS`, and `UNC_M3UPI_RING_BOUNCES_HORZ.AD`.
- Run perf PMU event tests under `tools/perf/tests/pmu-events.c` after generation to catch alias/table regressions.
- On a Skylake X host, `perf list` should expose representative `uncore_*` aliases with package-scope metadata, and `perf stat -e` should accept complete event names from the generated table.
- Chunk reconciliation should verify the next chunk completes the partial `UNC_M3UPI_RING_BOUNCES_HORZ.AK` object before producing the final per-file report.
