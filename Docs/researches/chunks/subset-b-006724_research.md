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
