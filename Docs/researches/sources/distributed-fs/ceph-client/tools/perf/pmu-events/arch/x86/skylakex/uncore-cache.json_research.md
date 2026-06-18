# Research: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-cache.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006723`: lines 1-5912, `Docs/researches/chunks/subset-b-006723_research.md`
- `subset-b-006724`: lines 5913-12883, `Docs/researches/chunks/subset-b-006724_research.md`
- `subset-b-006725`: lines 12884-12923, `Docs/researches/chunks/subset-b-006725_research.md`

## Chunk Research

### subset-b-006723: lines 1-5912

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-cache.json lines 1-5912

## Scope

This chunk covers the beginning of the Skylake-X perf PMU uncore cache event table. The full source is a JSON array of event descriptor objects; this chunk contains the opening `[` plus 537 complete `UNC_CHA_*` event objects and then stops inside the next object, after the `PerPkg` field for `UNC_CHA_TxR_VERT_CYCLES_NE.BL_AG0`. Adjacent chunks are required to complete that partially visible record and the rest of the file.

## Purpose

The file is data, not executable code. It declares Intel Skylake-X uncore cache/home-agent PMU events consumed by Linux `perf` so users can select symbolic event names instead of writing raw uncore event encodings. All complete events in this chunk have `Unit: "CHA"`, which `tools/perf/pmu-events/jevents.py` maps to the runtime PMU name `uncore_cha`.

These descriptors cover CHA clock ticks, RxC request queues, core snoops, LLC lookups and victims, TOR inserts/occupancy, IMC-facing requests, snoop responses, HITME/IODC state changes, mesh/ring use, CMS credits, TxR/RxR occupancy and insertion events, ring starvation/bounce events, and horizontal/vertical transmit-ring behavior.

## Data Model And Generated API Surface

Each complete object in this chunk follows the perf JSON event schema used by `jevents.py`:

- `EventName`: symbolic perf event name, lowercased by generation into `struct pmu_event.name`.
- `EventCode`: base hardware event selector, converted to `event=<value>`.
- `UMask`: event unit mask, converted to `umask=<value>` when nonzero.
- `BriefDescription`: short description used as `struct pmu_event.desc`.
- `PublicDescription`: longer help text used as `struct pmu_event.long_desc` when distinct.
- `Unit`: source PMU unit name; `CHA` becomes `uncore_cha`.
- `PerPkg`: package aggregation flag, stored as `struct pmu_event.perpkg`.
- `Counter`: metadata about legal CHA counter slots; most records use `0,1,2,3`, while 37 records use only `0`.
- Optional `Experimental`, `Deprecated`, and `Filter` fields are preserved into generated attributes where supported.

The relevant generated C API is declared in `tools/perf/pmu-events/pmu-events.h`. `struct pmu_event` is the runtime representation with `name`, `event`, `desc`, `topic`, `long_desc`, `pmu`, `unit`, `perpkg`, and `deprecated` fields. Generated lookup/iteration APIs include `pmu_events_table__for_each_event`, `pmu_events_table__find_event`, `pmu_events_table__num_events`, and `perf_pmu__find_events_table`.

## Generation And Control Flow

Build-time flow:

1. `jevents.py` scans architecture/model JSON files such as this one.
2. `read_json_events()` loads the array with Python `json.load(..., object_hook=JsonEvent)`.
3. `JsonEvent.__init__()` canonicalizes fields: it lowercases `EventName`, builds an encoded event string from `EventCode` plus nonzero `UMask` and filters, maps `Unit` to a Linux PMU name, and normalizes descriptions.
4. Event objects are accumulated, sorted by PMU/name, and emitted into compressed generated C tables.
5. At runtime, perf selects the model table through CPU/PMU matching and uses generated table functions to iterate or binary-search events under the matching PMU name.

Runtime flow for these records is therefore lookup-driven rather than file-read-driven. A user-facing event such as `uncore_cha/event=.../` or a symbolic `UNC_CHA_*` name resolves through the generated table for Skylake-X and the `uncore_cha` PMU.

## Event Families In This Chunk

The chunk contains 537 complete records across these families:

- CMS/agent credit families: `UNC_CHA_AG0_AD_CRD_ACQUIRED`, `UNC_CHA_AG0_AD_CRD_OCCUPANCY`, `UNC_CHA_AG1_AD_CRD_ACQUIRED`, `UNC_CHA_AG1_AD_CRD_OCCUPANCY`, `UNC_CHA_AG0_BL_CRD_ACQUIRED`, `UNC_CHA_AG0_BL_CRD_OCCUPANCY`, `UNC_CHA_AG1_BL_CREDITS_ACQUIRED`, and `UNC_CHA_AG1_BL_CRD_OCCUPANCY`, each split across transgress masks `TGR0` through `TGR5`.
- RxC queue pressure and retry families: occupancy, inserts, IRQ/PRQ/IPQ/ISMQ/RRQ/WBQ rejects, request queue retries, and other retries, generally split across VN, HA, victim, snoop, and non-UPI masks.
- Cache/snoop/TOR families: `UNC_CHA_CORE_SNP`, `UNC_CHA_LLC_LOOKUP`, `UNC_CHA_LLC_VICTIMS`, `UNC_CHA_TOR_INSERTS`, `UNC_CHA_TOR_OCCUPANCY`, `UNC_CHA_REQUESTS`, `UNC_CHA_SNOOPS_SENT`, `UNC_CHA_SNOOP_RESP`, and `UNC_CHA_SNOOP_RESP_LOCAL`.
- Memory-controller and directory adjacency: `UNC_CHA_IMC_READS_COUNT`, `UNC_CHA_IMC_WRITES_COUNT`, `UNC_CHA_DIR_LOOKUP`, `UNC_CHA_DIR_UPDATE`, `UNC_CHA_READ_NO_CREDITS`, `UNC_CHA_BYPASS_CHA_IMC`, and `UNC_CHA_OSB`.
- HITME/IODC/miscellaneous state: HITME lookup/hit/miss/update, IODC alloc/dealloc, SF eviction, MISC, FAST asserted, egress ordering, ring source throttling, and CHA/CMS clockticks.
- Mesh/ring transport: ring bounce and starvation families, horizontal ring in-use families, `RxR_*`, `TxR_HORZ_*`, `TxR_VERT_ADS_USED`, `TxR_VERT_BYPASS`, `TxR_VERT_CYCLES_FULL`, and the beginning of `TxR_VERT_CYCLES_NE`.

Important boundary detail: lines 5906-5912 begin `UNC_CHA_TxR_VERT_CYCLES_NE.BL_AG0` but the chunk omits its `PublicDescription`, `UMask`, `Unit`, and closing brace. The last complete event before that partial object is `UNC_CHA_TxR_VERT_CYCLES_NE.AK_AG1`.

## State And Persistence Behavior

This file has no mutable state, persistence writes, function calls, or side effects. Persistence happens through source control and through generated `pmu-events.c` style tables produced during the perf build. At runtime the data is static read-only metadata embedded in the perf binary or build output.

`PerPkg: "1"` is set on all complete records in this chunk, which signals package-level aggregation. That matters because CHA uncore counters are package-wide resources rather than per-thread core PMCs. Most records are also marked `Experimental: "1"`; 468 complete records have that flag, while 69 complete records omit it.

## Dependencies And Integration Points

Primary dependencies:

- Python JSON parsing in `tools/perf/pmu-events/jevents.py`.
- The perf PMU event schema represented by `tools/perf/pmu-events/pmu-events.h`.
- Linux uncore PMU naming conventions; `Unit: "CHA"` maps to `uncore_cha`.
- Skylake-X model directory discovery under `tools/perf/pmu-events/arch/x86/skylakex/`.
- Runtime perf PMU discovery and wildcard PMU-name matching when looking up generated event tables.

Integration points include `perf list` display, `perf stat` event selection, generated table lookup by `perf_pmu__find_events_table()`, and tests under `tools/perf/tests/pmu-events.c` that validate generated event table behavior against expected JSON-derived entries.

## Risks And Edge Cases

- Chunk boundary risk: this chunk is not independently valid JSON because it stops inside an event object. Research or merge tooling must not parse only lines 1-5912 as a standalone file.
- Event-name spelling is part of the public perf interface. The family `UNC_CHA_AG1_BL_CREDITS_ACQUIRED` uses `CREDITS` while neighboring families use `CRD`; changing that would break existing symbolic event names.
- Several descriptions appear mechanically repeated or inconsistent. For example, vertical `CYCLES_FULL` records say the egress was "Not Full" in their public descriptions, which conflicts with the event name. This may be inherited vendor text, but it is a documentation risk.
- Generated event strings depend on nonzero `UMask`; a missing or zero mask would collapse variants into the same raw event encoding.
- Counter-slot metadata is mixed: 500 complete records allow counters `0,1,2,3`; 37 allow only counter `0`. Tooling that ignores `Counter` could permit unsupported scheduling.
- The JSON uses string values for booleans/enums such as `PerPkg` and `Experimental`; schema consumers must preserve the expected conversion behavior.

## Test Signals

Useful validation for this chunk and the eventual merged file:

- `jq` should parse the full `uncore-cache.json` successfully; parsing only this chunk should fail because of the intentional chunk boundary.
- Generated perf events should include all complete names in this chunk under PMU `uncore_cha`, with event strings formed from `EventCode` and `UMask`.
- `perf list` on a Skylake-X-capable build should show these `UNC_CHA_*` names or their lowercased generated forms in the uncore CHA topic.
- Existing PMU event tests should continue to exercise `pmu_events_table__for_each_event`, `pmu_events_table__find_event`, and generated table counts.
- Spot checks should verify package aggregation for these records, preservation of `Deprecated` where present, and no duplicate `(EventCode, UMask, EventName)` collisions introduced by edits.

### subset-b-006724: lines 5913-12883

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-cache.json lines 5913-12883

## Scope

This chunk covers lines 5,913 through 12,883 of the Skylake Xeon `uncore-cache.json` perf PMU event table. The full source file has 12,923 lines and is a JSON array of event descriptor objects for Intel server uncore cache/home-agent PMUs. This range is a middle/tail chunk: it starts inside the already-open `UNC_CHA_TxR_VERT_CYCLES_NE.BL_AG0` object whose `EventName` appears at line 5,910, and it ends inside the deprecated `UNC_H_XSNP_RESP.EXT_RSPI_FWDM` object after `EventCode: 0x32` at line 12,883. The next lines, outside this work item, contain that object's `EventName`, flags, `UMask`, and `Unit`, followed by the remaining three deprecated `UNC_H_XSNP_RESP.EXT_*` objects and the closing array.

Within the assigned line window there are 637 visible `EventName` fields and 638 visible `Unit: CHA` fields. The off-by-one is expected because the first in-range lines complete an object that started before line 5,913. The chunk includes 550 `Deprecated: 1` markers, 598 `Experimental: 1` markers, 89 visible `PublicDescription` entries, 638 visible `BriefDescription` entries, 633 visible `UMask` entries, and no `ScaleUnit` or derived metric fields.

## Purpose

This file supplies Intel Skylake Xeon uncore cache PMU metadata to Linux perf. It is not executable Ceph or filesystem logic despite living under `sources/distributed-fs/ceph-client`; it is vendored Linux `tools/perf` data. The JSON objects are consumed by `tools/perf/pmu-events/jevents.py` during the perf build and converted into generated C tables used by `perf list`, `perf stat`, event alias lookup, and PMU documentation paths.

This chunk contributes the late CHA/home-agent event catalog. It covers Common Mesh Stop and home-agent traffic counters for vertical and horizontal ring use, egress queue occupancy and starvation, UPI credit accounting, TOR inserts/occupancy, LLC lookup/victim behavior, directory and snoop-filter activity, HITME state transitions, IMC read/write classes, request and snoop response families, RxC/RxR queue rejects/retries/occupancy, TxR ring inserts/NACKs/occupancy/starvation, write/read no-credit counters, and new-plus-deprecated cross-snoop response names. The data is important for server performance diagnosis around mesh congestion, cache coherence traffic, local versus remote access, snoop behavior, and memory-controller pressure.

## Data Shape And Important Fields

Each event object follows the perf PMU event JSON schema read by `jevents.py`:

- `EventName` is the symbolic event alias. `jevents.py` lowercases it for generated table matching, so `UNC_H_TxR_VERT_INSERTS.AD_AG0` becomes a lower-case perf alias while preserving the selector data.
- `EventCode` is parsed as the base hardware event selector and emitted as `event=<value>`. This chunk uses many selectors, including `0x90`-`0x98` for CHA/TxR egress families, `0x32` for cross-snoop response families, `0x35` and `0x36` for TOR insert/occupancy, `0x11`-`0x2f` for home-agent RxC/RxR families, and `0xb0`-`0xb4`/`0xd0`-`0xd6` for horizontal/vertical TxR stall families.
- `UMask` selects subevents such as ring, queue, request type, response type, target group, local/remote class, or coherence state. `jevents.py` translates non-zero `UMask` values to `umask=<value>` in the generated event string.
- `Counter` is almost always `0,1,2,3` in this range, meaning the events are generally available on the four programmable CHA counters.
- `Unit` is always `CHA` in the visible range. `jevents.py` maps unknown units by lowercasing with an `uncore_` prefix, so these entries bind to the `uncore_cha` PMU naming convention.
- `PerPkg: 1` appears on all visible complete events except the object cut at the chunk end. It marks package-scoped uncore accounting.
- `Experimental: 1` appears on many CHA event families and on the deprecated `UNC_H_*` aliases. These aliases are user-visible but less stable than ordinary architectural events.
- `Deprecated: 1` is concentrated in the `UNC_C_*` and `UNC_H_*` compatibility sections. The corresponding `BriefDescription` usually says to use a newer `UNC_CHA_*` event.
- `BriefDescription` supplies the short `perf list` text. `PublicDescription` is present mostly in the active `UNC_CHA_*` families near the chunk start; many deprecated aliases intentionally have only a short deprecation message.

There are no `MetricName`, `MetricExpr`, threshold, aggregation, or scale-unit fields in this chunk, so it defines raw hardware events rather than perf metrics.

## Event Families In This Chunk

The chunk starts by finishing the active `UNC_CHA_TxR_VERT_CYCLES_NE` family. The previous chunk contains the earlier AD/AK/BL Agent 0 records; this range includes the tail of `BL_AG0`, then `BL_AG1` and `IV`. It then defines complete active CHA vertical TxR families: `UNC_CHA_TxR_VERT_INSERTS`, `UNC_CHA_TxR_VERT_NACK`, `UNC_CHA_TxR_VERT_OCCUPANCY`, and `UNC_CHA_TxR_VERT_STARVED`. These describe Common Mesh Stop vertical egress allocations, NACKs, occupancy, and starvation across AD, AK, BL, and IV rings with Agent 0 and Agent 1 variants where applicable.

`UNC_CHA_UPI_CREDITS_ACQUIRED` and `UNC_CHA_UPI_CREDIT_OCCUPANCY` count UPI credit acquisition and in-use states for AD request/response, BL NCB/NCS/response/writeback, VN0, and VNA credit classes. They expose fabric backpressure signals that can separate demand pressure from writeback or non-coherent traffic.

`UNC_CHA_VERT_RING_AD_IN_USE`, `UNC_CHA_VERT_RING_AK_IN_USE`, `UNC_CHA_VERT_RING_BL_IN_USE`, and `UNC_CHA_VERT_RING_IV_IN_USE` measure vertical ring use by direction and parity-like lane classes (`DN_EVEN`, `DN_ODD`, `UP_EVEN`, `UP_ODD`) or simpler `DN`/`UP` variants for IV. `UNC_CHA_WB_PUSH_MTOI` distinguishes writeback push M-to-I traffic to LLC versus memory, and `UNC_CHA_WRITE_NO_CREDITS` reports write-credit starvation for EDC and memory-controller SMI targets.

`UNC_CHA_XSNP_RESP` is the active cross-snoop response family in this range. It covers `ANY`, `CORE`, `EVICT`, and `EXT` sources with response variants such as `RSPI`, `RSPS`, forwarded exclusive/modified forms (`FWDFE`, `FWDM`), and `RSP_HITFSE`. These events are the preferred replacements for the deprecated `UNC_H_XSNP_RESP` aliases near the end of the chunk.

The `UNC_C_*` block is primarily deprecated compatibility naming. `UNC_C_CLOCKTICKS`, `UNC_C_FAST_ASSERTED`, `UNC_C_LLC_LOOKUP`, `UNC_C_LLC_VICTIMS`, `UNC_C_RING_SRC_THRTL`, `UNC_C_TOR_INSERTS`, and `UNC_C_TOR_OCCUPANCY` point users toward `UNC_CHA_*` names. Despite deprecation, the objects still encode counters, event selectors, masks, package scope, and `Unit: CHA`.

The `UNC_H_*` block is much larger and describes home-agent oriented compatibility aliases. Credit families such as `UNC_H_AG0_AD_CRD_ACQUIRED`, `UNC_H_AG0_AD_CRD_OCCUPANCY`, `UNC_H_AG0_BL_CRD_ACQUIRED`, `UNC_H_AG0_BL_CRD_OCCUPANCY`, `UNC_H_AG1_AD_CRD_ACQUIRED`, `UNC_H_AG1_AD_CRD_OCCUPANCY`, `UNC_H_AG1_BL_CRD_OCCUPANCY`, and `UNC_H_AG1_BL_CREDITS_ACQUIRED` are split by transgress `TGR0` through `TGR5`.

Home-agent cache/coherence families include `UNC_H_CORE_PMA`, `UNC_H_CORE_SNP`, `UNC_H_DIR_LOOKUP`, `UNC_H_DIR_UPDATE`, `UNC_H_HITME_HIT`, `UNC_H_HITME_LOOKUP`, `UNC_H_HITME_MISS`, `UNC_H_HITME_UPDATE`, `UNC_H_SF_EVICTION`, `UNC_H_SNOOPS_SENT`, `UNC_H_SNOOP_RESP`, and `UNC_H_SNP_RSP_RCV_LOCAL`. These classify low-power/core PMA states, snoop fanout, directory lookup/update behavior, HITME ownership transitions, snoop-filter eviction states, and local snoop response classes.

Ring and memory-side families include `UNC_H_HORZ_RING_*_IN_USE`, `UNC_H_VERT_RING_*_IN_USE`, `UNC_H_RING_BOUNCES_HORZ`, `UNC_H_RING_BOUNCES_VERT`, `UNC_H_RING_SINK_STARVED_HORZ`, `UNC_H_RING_SINK_STARVED_VERT`, `UNC_H_IMC_READS_COUNT`, `UNC_H_IMC_WRITES_COUNT`, `UNC_H_READ_NO_CREDITS`, `UNC_H_WRITE_NO_CREDITS`, `UNC_H_REQUESTS`, and `UNC_H_WB_PUSH_MTOI`. They expose direction, ring type, controller target, read/write priority, local/remote request, and memory-controller backpressure dimensions.

The RxC/RxR sections are the densest part of the chunk. `UNC_H_RxC_INSERTS`, `UNC_H_RxC_*_REJECT`, `UNC_H_RxC_*_RETRY`, and `UNC_H_RxC_OCCUPANCY` distinguish IPQ, IRQ, ISMQ, PRQ, RRQ, WBQ, request queue, and other queue paths. Many `*_0_*` families break out virtual network classes such as `AD_REQ_VN0`, `AD_RSP_VN0`, `BL_NCB_VN0`, `BL_NCS_VN0`, `BL_RSP_VN0`, and `BL_WB_VN0`; many `*_1_*` families classify rejection or retry causes such as `ALLOW_SNP`, `HA`, `LLC_OR_SF_WAY`, `LLC_VICTIM`, `PA_MATCH`, `SF_VICTIM`, and `VICTIM`. `UNC_H_RxR_BUSY_STARVED`, `UNC_H_RxR_BYPASS`, `UNC_H_RxR_CRD_STARVED`, `UNC_H_RxR_INSERTS`, and `UNC_H_RxR_OCCUPANCY` then describe received ring buffer behavior for AD/AK/BL/IV bounce and credit paths.

The TxR home-agent section mirrors egress behavior for horizontal and vertical rings. Horizontal families include `UNC_H_STALL_NO_TxR_HORZ_CRD_*`, `UNC_H_TxR_HORZ_ADS_USED`, `UNC_H_TxR_HORZ_BYPASS`, `UNC_H_TxR_HORZ_CYCLES_FULL`, `UNC_H_TxR_HORZ_CYCLES_NE`, `UNC_H_TxR_HORZ_INSERTS`, `UNC_H_TxR_HORZ_NACK`, `UNC_H_TxR_HORZ_OCCUPANCY`, and `UNC_H_TxR_HORZ_STARVED`. Vertical families include `UNC_H_TxR_VERT_ADS_USED`, `UNC_H_TxR_VERT_BYPASS`, `UNC_H_TxR_VERT_CYCLES_FULL`, `UNC_H_TxR_VERT_CYCLES_NE`, `UNC_H_TxR_VERT_INSERTS`, `UNC_H_TxR_VERT_NACK`, `UNC_H_TxR_VERT_OCCUPANCY`, and `UNC_H_TxR_VERT_STARVED`. Their suffixes separate AD/AK/BL/IV, bounce versus credit paths, and Agent 0/Agent 1 where the hardware model exposes that dimension.

The visible tail is the deprecated `UNC_H_XSNP_RESP` family. The chunk includes aliases through `EXT_RSPI_FWDFE` and starts `EXT_RSPI_FWDM` but stops before that object's `EventName` line. These aliases refer users to `UNC_CHA_XSNP_RESP.*` replacements and reuse selector `0x32` with masks matching the active cross-snoop response family.

## Control Flow And Integration

There is no local control flow in the JSON itself. The effective flow is the perf PMU event generation path:

1. The perf build traverses `tools/perf/pmu-events/arch/x86/skylakex`.
2. `jevents.py` opens each JSON file, parses every event object, and constructs `JsonEvent` instances.
3. `JsonEvent` lowercases `EventName`, maps `Unit` to a PMU name, normalizes `EventCode` and `UMask`, preserves fields such as `deprecated` and `perpkg`, and copies `BriefDescription`/`PublicDescription` into short and long descriptions.
4. The generated PMU event C tables are compiled into perf.
5. Runtime perf PMU lookup selects the Skylake Xeon model through the x86 mapfile and exposes these `uncore_cha` aliases for `perf list`, `perf stat -e`, and related parser paths.

The strongest integration point is the `Unit: CHA` to PMU-name conversion. In `jevents.py`, units not in the explicit table become `uncore_<lowercase-unit>`, so this chunk's events are expected to bind to kernel PMUs named like `uncore_cha_*`. If kernel naming or model matching changes, these JSON aliases can remain generated but fail to match real PMU instances on target hardware.

## State And Persistence Behavior

The source file is static build-time metadata. It does not maintain runtime state, open files, allocate resources, or persist measurements. Its persistent effects are indirect:

- Generated perf event tables change when this JSON changes.
- User-visible event names and descriptions in `perf list` change with the generated tables.
- The `Deprecated: 1` and `Experimental: 1` flags persist into generated metadata and should influence UI/test expectations.
- `PerPkg: 1` preserves package-level semantics for uncore counters; counts should not be interpreted as thread-local or core-local values.

Runtime counter state lives in hardware CHA PMU registers and in perf event file descriptors/kernel data structures, not in the JSON.

## Dependencies

This chunk depends on:

- The perf PMU event schema supported by `tools/perf/pmu-events/jevents.py`, especially parsing of `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `Deprecated`, `Experimental`, and description fields.
- x86 model selection through `tools/perf/pmu-events/arch/x86/mapfile.csv`, which must map Skylake Xeon CPU IDs to the `skylakex` event directory.
- Kernel uncore CHA PMU support that exposes PMU instances compatible with generated `uncore_cha` aliases and accepts the event/umask encodings.
- Full-file JSON validity. This chunk cannot be parsed standalone because both boundaries split event objects.
- Compatibility expectations for deprecated aliases. Existing users or tests may still refer to `UNC_C_*` or `UNC_H_*` names even when descriptions point to `UNC_CHA_*` replacements.

## Risks And Edge Cases

Both chunk boundaries cut through JSON objects. A reconciliation or merge lane must stitch this report with adjacent chunks and must not try to validate lines 5,913-12,883 as a standalone JSON array. The first visible object lacks its in-range `EventName`, `Counter`, and `EventCode`; the last visible object lacks its in-range `EventName`, `Experimental`, `PerPkg`, `UMask`, and `Unit`.

The chunk contains many deprecated aliases. Removing them because replacement names exist would be a user-facing compatibility break for scripts that still use `UNC_C_*` or `UNC_H_*` symbols.

The event matrix is highly repetitive but not uniform. Similar-looking families differ by selector, mask, queue, ring, target group, direction, or response type. Bulk edits are risky because a one-character suffix or mask swap can silently redirect users to a different hardware condition.

Several families encode hardware topology in suffixes rather than separate structured fields: `AG0`/`AG1`, `AD`/`AK`/`BL`/`IV`, `DN`/`UP`, `LEFT`/`RIGHT`, `TGR0`-`TGR5`, `VN0`/`VNA`, local/remote, and memory-controller SMI target. Renaming or normalizing suffixes would alter the public perf alias contract.

Many entries have `Experimental: 1`, so test baselines should allow that these events may be less stable than non-experimental PMU aliases. At the same time, the generated parser treats them as normal alias rows, so malformed fields still break generation or runtime lookup.

Most deprecated entries lack `PublicDescription`, so generated long descriptions may be absent even though short descriptions exist. That is expected and should not be mistaken for incomplete parsing.

## Test Signals

Useful validation signals for this chunk and the eventual merged per-file report:

- Validate the complete `uncore-cache.json` file as JSON after all chunks are considered; this line range alone is intentionally incomplete JSON.
- Re-run the perf PMU event generator path, especially `tools/perf/pmu-events/jevents.py`, and ensure generated tables include representative aliases from this range.
- Run perf PMU event tests such as `tools/perf/tests/pmu-events.c` and parser tests that compare generated event metadata against expected `pmu_event` fields.
- Inspect generated aliases for representative active events: `unc_cha_txr_vert_inserts.ad_ag0`, `unc_cha_upi_credits_acquired.bl_wb`, `unc_cha_xsnp_resp.any_rspi_fwdfe`, `unc_cha_vert_ring_bl_in_use.up_even`, and `unc_cha_write_no_credits.mc0_smi0`.
- Inspect generated aliases for representative deprecated compatibility names: `unc_c_llc_lookup.any`, `unc_c_tor_inserts.ipq`, `unc_h_rxc_ipq1_reject.llc_victim`, `unc_h_txr_vert_occupancy.bl_ag1`, and `unc_h_xsnp_resp.evict_rsps_fwdm`.
- On Skylake Xeon hardware, smoke-test a small set with `perf stat -e` against real `uncore_cha_*` PMUs and verify counts are package-scope and accepted by the kernel PMU driver.
- Diff generated `pmu-events.c` or equivalent generated artifacts after any JSON edit to catch unintended changes in event selectors, masks, `deprecated`, `perpkg`, or descriptions.

### subset-b-006725: lines 12884-12923

# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-cache.json lines 12884-12923

## Scope

This chunk covers the final 40 lines of the Skylake Xeon `uncore-cache.json` PMU event table in the vendored Linux `tools/perf` tree. The file is static JSON metadata, not executable program logic. Perf's PMU event generator reads these records and emits compiled event tables so users can request Intel uncore events by symbolic names.

The requested range starts in the middle of a JSON object. Lines 12880-12883, just before this chunk, contain the opening fields for `UNC_H_XSNP_RESP.EXT_RSPI_FWDM`: `BriefDescription`, `Counter`, `Deprecated`, and `EventCode`. Lines 12884-12889 finish that object. The chunk then contains two complete deprecated external-response objects and the final complete deprecated hit object before closing the JSON array at line 12923.

## Purpose

The events in this slice preserve legacy `UNC_H_XSNP_RESP.*` names for core cross-snoop response counters and redirect users to the newer `UNC_CHA_XSNP_RESP.*` naming scheme. They are compatibility aliases for Skylake Xeon CHA uncore PMU events. The aliases remain programmable because they retain the same hardware selector fields as the replacement `UNC_CHA_XSNP_RESP.*` definitions, while the `Deprecated` marker and descriptions tell users to migrate.

The visible events are:

- `UNC_H_XSNP_RESP.EXT_RSPI_FWDM`, partially visible in this chunk, deprecated in favor of `UNC_CHA_XSNP_RESP.EXT_RSPI_FWDM`, with `EventCode: "0x32"` and `UMask: "0x30"`.
- `UNC_H_XSNP_RESP.EXT_RSPS_FWDFE`, deprecated in favor of `UNC_CHA_XSNP_RESP.EXT_RSPS_FWDFE`, with `EventCode: "0x32"` and `UMask: "0x22"`.
- `UNC_H_XSNP_RESP.EXT_RSPS_FWDM`, deprecated in favor of `UNC_CHA_XSNP_RESP.EXT_RSPS_FWDM`, with `EventCode: "0x32"` and `UMask: "0x28"`.
- `UNC_H_XSNP_RESP.EXT_RSP_HITFSE`, deprecated in favor of `UNC_CHA_XSNP_RESP.EXT_RSP_HITFSE`, with `EventCode: "0x32"` and `UMask: "0x21"`.

Earlier full replacement records in the same file describe these as external-request cross-snoop response filters. They count core cross snoops where a cache lookup determines snooping is necessary, then filter by response state transition: response I to forwarded M, response S to forwarded F/E, response S to forwarded M, or any response to hit F/S/E.

## Important Data Fields

Each object uses the perf PMU event JSON schema used under `tools/perf/pmu-events`:

- `EventName` is the symbolic event exposed through perf's generated event tables. In this chunk the names use the legacy `UNC_H_XSNP_RESP` prefix.
- `BriefDescription` is user-facing text shown by perf and, for these aliases, carries the deprecation redirect to the corresponding `UNC_CHA_XSNP_RESP` event.
- `Counter` is `"0,1,2,3"` for the complete visible objects and for the partially visible first object from the preceding lines. These events can be scheduled on any listed CHA uncore counter.
- `Deprecated` is `"1"` for every visible alias, causing the generated `struct pmu_event` to carry deprecation metadata.
- `EventCode` is `"0x32"` for this cross-snoop response event family.
- `UMask` selects the external request and response subtype. The visible masks are `0x30`, `0x22`, `0x28`, and `0x21`.
- `Experimental` is `"1"` for every visible alias, warning that the metadata is marked experimental in this vendored perf table.
- `PerPkg` is `"1"`, so measurements are package-scoped uncore events rather than thread-local counters.
- `Unit` is `"CHA"`, binding the aliases to Intel Cache/Home Agent uncore PMUs.

There is no `PublicDescription` in these deprecated alias records. The non-deprecated `UNC_CHA_XSNP_RESP.*` records earlier in the file carry longer descriptions for the same event code and masks.

## APIs, Types, And Generated Representation

This JSON file does not define local functions, classes, or C types. Its effective API is the generated perf PMU event table:

- `tools/perf/pmu-events/jevents.py` reads JSON event files under `tools/perf/pmu-events/arch/<arch>/<model>/`.
- The generated C uses `struct pmu_event` from `tools/perf/pmu-events/pmu-events.h`, including fields such as `name`, `event`, `desc`, `pmu`, `unit`, `perpkg`, and `deprecated`.
- `pmu_events_table__for_each_event()` iterates generated events for listing and alias setup.
- `pmu_events_table__find_event()` resolves a symbolic event name, such as `UNC_H_XSNP_RESP.EXT_RSPS_FWDM`, against the generated table.
- Runtime perf code then maps the generated alias to the hardware event selector string built from `EventCode`, `UMask`, and related fields.

For this chunk, `Deprecated`, `EventCode`, `UMask`, `Unit`, and `PerPkg` are the important generated semantics. The event aliases should still resolve, but consumers should prefer the replacement `UNC_CHA_XSNP_RESP.*` names.

## Control Flow

The JSON has no direct control flow. Its build-time and runtime flow is:

1. The perf build runs the PMU event generation path before building the perf binary.
2. `jevents.py` traverses the Skylake Xeon JSON files, including `arch/x86/skylakex/uncore-cache.json`.
3. The generator parses the event objects, including these final deprecated aliases, and emits generated PMU event table data.
4. `pmu-events.c` is compiled into the perf build.
5. At runtime, perf matches the running x86 CPU against `arch/x86/mapfile.csv`; Skylake Xeon CPUIDs matching `GenuineIntel-6-55-[01234]` map to the `skylakex` directory in this tree.
6. `perf list` can display the legacy alias names, with deprecation metadata available from the generated table.
7. `perf stat -e <event>` resolves the alias and programs the package-level CHA uncore PMU counter using event code `0x32` plus the selected mask.

Within the full file, these records are part of a final compatibility block of `UNC_H_*` aliases. This chunk specifically closes the external-request subfamily and then closes the top-level JSON array.

## State And Persistence Behavior

Persistent state is limited to checked-in JSON metadata and any generated `pmu-events.c` output created during the perf build. The source file itself does not create files, maintain mutable process state, or store measurements.

Runtime state lives in hardware uncore counters on supported Skylake Xeon systems. Because `PerPkg` is set, counts are package-level CHA measurements. Because these are cross-snoop response filters, the measured state reflects cache/home-agent snoop response activity for external requests, split by the selected response category.

The deprecation state is also persistent metadata. `Deprecated: "1"` lets downstream perf UI and table consumers distinguish these legacy aliases from the preferred `UNC_CHA_XSNP_RESP.*` records. Removing these aliases would be a user-visible compatibility change for scripts that still use `UNC_H_XSNP_RESP.*` event names.

## Dependencies And Integration Points

This chunk integrates with the Linux perf PMU event stack:

- `tools/perf/pmu-events/README` documents the JSON input format, model directories, `mapfile.csv`, and generation of `pmu-events.c`.
- `tools/perf/pmu-events/jevents.py` consumes the JSON and emits generated C event tables.
- `tools/perf/pmu-events/pmu-events.h` defines `struct pmu_event` and table lookup APIs used by the generated data.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` maps Skylake Xeon CPU IDs to the `skylakex` model directory.
- The x86 uncore PMU driver must expose CHA PMUs and counters compatible with event code `0x32` for the aliases to count on hardware.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file belongs to a vendored Linux perf tooling subtree. It has no direct integration with CephFS client control flow, distributed filesystem metadata state, network protocols, or storage persistence.

## Risks And Edge Cases

The first record is partial in this chunk. A line-range-only reader sees `EventName`, `Experimental`, `PerPkg`, `UMask`, and `Unit` for `UNC_H_XSNP_RESP.EXT_RSPI_FWDM`, but its deprecation description, counter list, deprecated flag, and event code are on immediately preceding lines. The later merge lane must use adjacent chunk context before validating complete object coverage.

The chunk is the end of the JSON array. Any edit here must preserve valid comma placement: the final object has no trailing comma and is followed by `]`. A syntax error at this tail would prevent `jevents.py` from parsing the whole `uncore-cache.json` file.

The compatibility aliases intentionally duplicate the replacement events' selector values. A mismatched `UMask` between `UNC_H_XSNP_RESP.EXT_RSPS_FWDM` and `UNC_CHA_XSNP_RESP.EXT_RSPS_FWDM`, for example, would silently make the deprecated alias count a different snoop-response class than its replacement. The visible masks match the earlier replacement records in this file.

All visible aliases are marked both deprecated and experimental. Users may still rely on them for old scripts, but new documentation and examples should prefer `UNC_CHA_XSNP_RESP.*`.

The brief deprecation strings are the only explanatory text in these alias records. If perf UI suppresses deprecated events by default or does not show `BriefDescription`, users may not see the migration target unless they ask for detailed listings.

## Test Signals

Useful validation signals for this chunk include:

- Run JSON validation on the complete `skylakex/uncore-cache.json`, not just this partial line range.
- Run the perf PMU event generation path and confirm `jevents.py` accepts the file and emits generated event-table entries.
- Build perf and confirm `struct pmu_event` records for the four visible `UNC_H_XSNP_RESP.EXT_*` aliases carry `deprecated = true`, `perpkg = true`, and `unit = "CHA"`.
- Use generated-table lookup tests or a local perf build to confirm both old and new names resolve, for example `UNC_H_XSNP_RESP.EXT_RSPS_FWDFE` and `UNC_CHA_XSNP_RESP.EXT_RSPS_FWDFE`.
- Compare generated selector strings for each alias against its replacement event to ensure `event=0x32` and the same `umask` are preserved.
- On Skylake Xeon hardware with CHA uncore PMUs exposed, run package-wide `perf stat` for a representative deprecated alias and its `UNC_CHA_*` replacement under the same workload and confirm scheduling succeeds and counts are consistent.

## Cross-Chunk Notes

This document intentionally covers only lines 12884-12923. Earlier chunks contain the complete beginning of `UNC_H_XSNP_RESP.EXT_RSPI_FWDM`, the rest of the deprecated `UNC_H_XSNP_RESP.*` compatibility block, and the primary `UNC_CHA_XSNP_RESP.*` replacement records with full public descriptions. The final per-file research document should merge those views before making whole-file claims about all `UNC_H` aliases or all cross-snoop response event variants.
