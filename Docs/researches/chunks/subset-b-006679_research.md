# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-cache.json lines 5371-10335

## Scope

This chunk covers lines 5371-10335 of the Ice Lake Xeon `uncore-cache.json` PMU event table. The file is declarative perf metadata, not executable Ceph client code. It is stored under a repository snapshot of Linux `tools/perf/pmu-events/arch/x86/icelakex/` and feeds Linux perf's PMU event table generation for Ice Lake server uncore cache/home-agent events.

The selected range is a chunked view of one large JSON array. It is not a standalone JSON document: line 5371 starts inside the object for `UNC_CHA_RxC_WBQ1_REJECT.LLC_OR_SF_WAY`, and line 10335 ends inside the object for `UNC_CHA_TxR_HORZ_CYCLES_NE.BL_ALL`. The full source file has 11,977 lines, contains 1,111 JSON array entries, and parses as valid JSON. This slice exposes 462 `EventName` fields, all for the `CHA` uncore PMU unit.

The chunk is dominated by two large CHA TOR families:

- `UNC_CHA_TOR_INSERTS`: 166 records, event code `0x35`, counting successful TOR insertions that match a subevent qualification.
- `UNC_CHA_TOR_OCCUPANCY`: 143 records, event code `0x36`, accumulating valid TOR entries per cycle for matching subevent qualifications.

The remaining records cover WBQ retry causes, receive-ring ingress/egress pressure, snoop behavior, snoop-filter eviction states, horizontal mesh transmit pressure, and target-group credit stalls.

## Purpose

The purpose of this chunk is to expose Ice Lake Xeon CHA performance events to perf users. CHA events measure package-level behavior around cache/home-agent queues, snoop filter state, transaction order queues, and mesh stop traffic. These counters are useful for diagnosing LLC/SF conflicts, snoop traffic, memory access locality, PMem-vs-DDR routing, streaming writes, IO-originated transactions, and mesh backpressure.

The range starts with the tail of `UNC_CHA_RxC_WBQ1_REJECT`, which reports writeback queue retries by rejection cause:

- LLC or snoop-filter way conflict.
- LLC victim and snoop-filter victim cases.
- Physical-address match against an outstanding rejected request.
- Generic victim-related retry conditions.

It then describes CMS receive-side events:

- `UNC_CHA_RxR_BUSY_STARVED` counts ingress starvation caused by another queue having priority.
- `UNC_CHA_RxR_BYPASS` counts packets bypassing CMS ingress.
- `UNC_CHA_RxR_CRD_STARVED` and `UNC_CHA_RxR_CRD_STARVED_1` count ingress starvation caused by lack of credit forwarding toward egress.
- `UNC_CHA_RxR_INSERTS` counts CMS ingress allocations.
- `UNC_CHA_RxR_OCCUPANCY` tracks CMS ingress-buffer occupancy.

The middle section provides snoop and snoop-filter visibility:

- `UNC_CHA_SF_EVICTION` splits snoop-filter evictions by E, M, and S states.
- `UNC_CHA_SNOOPS_SENT` splits snoops by local/remote and broadcast/direct delivery.
- `UNC_CHA_SNOOP_RESP` and `UNC_CHA_SNOOP_RESP_LOCAL` classify responses such as conflict, forwarded data, forwarded writeback, invalid, shared, and writeback responses.
- `UNC_CHA_SNOOP_RSP_MISC` captures partial and modified-response cases that hit LLC or snoop filter.

The largest sections are the TOR insert and TOR occupancy families. They expose the same conceptual qualifiers in two measurement modes: inserts are event counts; occupancy accumulates valid matching entries each cycle. The qualifiers include:

- All, hit, miss, eviction, local target, remote target, near memory, not-near memory, DDR, PMM, and non-coherent traffic.
- iA-originated traffic, including CLFLUSH/CLFLUSHOPT, clean reads, demand reads, page-table reads, RFO, ITOM, SpecITOM, LLC prefetch code/data/RFO, writeback state transitions, WCIL/WCILF/WIL, and streaming write variants.
- Local and remote splits for clean reads, RFO, WCIL/WCILF, full streaming writes, partial streaming writes, DDR, DRAM, and PMM.
- IO-originated traffic, including PCI read current, RFO, ITOM, ITOMCACHENEAR, writeback modified-to-invalid, hit/miss splits, and local/remote variants in the inserts family.
- IPQ, PRQ, RRQ, WBQ, IRQ from iA and non-iA, ISOC, MMCFG, opcode-match, and pre-morphed opcode-match filters.

The tail of the range starts horizontal transmit-ring events:

- `UNC_CHA_TxR_HORZ_ADS_USED` counts use of horizontal anti-deadlock slots.
- `UNC_CHA_TxR_HORZ_BYPASS` counts packets bypassing horizontal egress.
- `UNC_CHA_TxR_HORZ_CYCLES_FULL` counts cycles where horizontal egress queues are full.
- `UNC_CHA_TxR_HORZ_CYCLES_NE` begins the not-empty queue family and continues past this chunk boundary.

## Important Schema Fields and Event Families

Each JSON object uses the standard perf PMU event metadata schema:

- `EventName`: the symbolic perf event name, such as `UNC_CHA_TOR_INSERTS.IA_MISS_DRD_LOCAL_DDR`.
- `EventCode`: the hardware event selector. This chunk uses selectors including `0x29`, `0x35`, `0x36`, `0x3D`, `0x51`, `0x5C`, `0x5D`, `0x6B`, `0xA2`, `0xA3`, `0xA6`, `0xA7`, `0xD0`-`0xD7`, `0xE0`-`0xE5`, and one lowercase `0xe4`.
- `UMask`: the unit mask or extended umask selecting traffic class, source, target, hit/miss mode, memory type, opcode-match mode, or target group. Some records intentionally omit `UMask`.
- `BriefDescription`: short human-readable summary.
- `PublicDescription`: longer explanation; this chunk has 447 `PublicDescription` fields across 462 event names.
- `Counter`: allowed counters. Most records use `0,1,2,3`; TOR occupancy records use counter `0` only.
- `Unit`: `CHA` for every event in this chunk.
- `PerPkg`: package-scope marker, normally `1`.
- `Experimental`: present on 379 records in this slice.
- `Deprecated`: present on 9 records, including the deprecated `UNC_CHA_TOR_INSERTS.DDR4` alias.

Major event-code groupings visible in the range are:

- `0x29`: `UNC_CHA_RxC_WBQ1_REJECT`, 5 records.
- `0xE0`-`0xE5` and `0xe4`: CMS receive-ring ingress occupancy, insert, bypass, credit-starved, and busy-starved families.
- `0x3D`, `0x51`, `0x5C`, `0x5D`, and `0x6B`: snoop-filter eviction, snoops sent, snoop responses, local snoop responses, and miscellaneous snoop response cases.
- `0xD0`-`0xD7`: horizontal TxR credit-stall target-group families for AD and BL, agent groups 0/1, and target groups `TGR0`-`TGR10`.
- `0x35`: TOR insert events, 166 records.
- `0x36`: TOR occupancy events, 143 records.
- `0xA6`, `0xA7`, `0xA2`, and `0xA3`: horizontal TxR ADS-used, bypass, full-cycle, and not-empty-cycle families.

The common traffic-class suffixes in CMS and TxR records are `AD_ALL`, `AD_CRD`, `AD_UNCRD`, `AK`, `AKC_UNCRD`, `BL_ALL`, `BL_CRD`, `BL_UNCRD`, and `IV`. Target-group stall records use suffixes such as `TGR0` through `TGR10`, with separate base names encoding AD/BL and agent group.

## Control Flow

There is no local control flow in this JSON file. Runtime behavior is table-driven:

1. Perf build tooling reads architecture-specific PMU event JSON files under `tools/perf/pmu-events/arch/x86/`.
2. The Ice Lake Xeon event records are validated and converted into generated event tables.
3. At runtime, perf selects the matching CPU model and exposes matching `EventName` values through interfaces such as `perf list`.
4. When a user requests one of these symbolic events, perf resolves it to `EventCode`, `UMask`, `Unit`, `Counter`, and package-scope metadata.
5. The kernel uncore PMU support programs CHA counters on available package/home-agent instances and perf reports counts back to the user.

Within this chunk, the data layout encodes several repeated control patterns. A base event code identifies a hardware counter source, while suffix and umask select a subcondition. For example, `UNC_CHA_RxR_INSERTS.*` records share event code `0xE1` and differ by traffic class masks, while `UNC_CHA_TOR_INSERTS.*` records share `0x35` and use extended masks to qualify origin, opcode, hit/miss state, memory target, locality, and request type. `UNC_CHA_TOR_OCCUPANCY.*` mirrors many insert qualifiers with event code `0x36`, but occupancy is restricted to counter `0`.

## State and Persistence Behavior

The persistent state is the checked-in JSON metadata. The file does not allocate memory, perform I/O, mutate runtime process state, or store measurement results. Measurement state lives in hardware counters after perf programs them.

All records in this chunk are package-scoped CHA events, so consumers should treat counts as uncore/package activity rather than per-thread execution. The same package can expose multiple CHA instances; aggregation and filtering behavior depends on perf's uncore PMU implementation and the user's event syntax.

Counter availability is part of the state contract. The 319 non-occupancy records in this slice generally allow counters `0,1,2,3`, while the 143 TOR occupancy records allow only counter `0`. Event groups that overconstrain a single CHA PMU can fail to schedule or be multiplexed by perf.

The chunk boundaries are persistence hazards for downstream merge tooling. The first complete object begins before line 5371, and the last object continues after line 10335. Any final per-file report or validator must parse the full file, not the chunk as a standalone JSON fragment.

## Dependencies and Integration Points

This file integrates with Linux perf, not directly with CephFS runtime code. Key integration points are:

- Perf's PMU event JSON parser and generator, which expect full-file valid JSON and known schema keys.
- The `icelakex` CPU model mapping in the perf PMU events tree, which determines when these Ice Lake Xeon events are exposed.
- Kernel/perf support for CHA uncore PMUs, including package-scope counter discovery, counter constraints, and event programming.
- User-facing perf commands such as `perf list`, `perf stat -e`, and generated event documentation.
- Intel Ice Lake server uncore event definitions, which are the source of truth for event codes, umasks, descriptions, counter constraints, and deprecated aliases.
- Adjacent chunks of the same file. Earlier lines define the opening of the first WBQ reject object and preceding event families; later lines complete `UNC_CHA_TxR_HORZ_CYCLES_NE.BL_ALL` and continue the rest of the `uncore-cache.json` table.

For repository research, this chunk should merge into a final source-tree-aligned report for `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-cache.json` after all chunks for that file are complete.

## Risks and Edge Cases

The highest risk is silent metadata error. A wrong event code or umask can program a different hardware condition while still returning plausible counts. This is especially likely in this range because hundreds of TOR records differ only by long suffixes and extended masks.

The TOR families are easy to misinterpret. `UNC_CHA_TOR_INSERTS.*` counts entries inserted into TOR, while `UNC_CHA_TOR_OCCUPANCY.*` accumulates matching valid entries each cycle. Occupancy values are not raw request counts and generally need normalization by cycles, CHA count, and workload duration.

Some fields are intentionally absent or uneven. Several TOR qualifiers such as `DDR`, `HIT`, `MISS`, `MMCFG`, `NEARMEM`, `PMM`, and opcode-match variants omit `UMask` in this slice, while neighboring records carry large extended masks. Custom schema checks must distinguish valid optional omissions from accidental data loss. Descriptions are also repetitive and sometimes rely on hardware-documentation vocabulary that is not self-contained.

Deprecated and experimental markers matter. The chunk includes deprecated records such as `UNC_CHA_TOR_INSERTS.DDR4`, and most records are marked experimental. Tooling should preserve these flags so perf can warn or filter appropriately.

Counter constraints are uneven. TOR occupancy records are counter-0-only, while many surrounding records use any of counters 0-3. A perf command grouping multiple counter-0-only occupancy events may fail or multiplex differently than a group of insert events.

Line-range chunking is an edge case. Since this requested chunk starts and ends inside object bodies, line-local JSON parsing will fail even though the complete source file is valid. Research and validation should use full-file parsing plus line-aware inspection.

## Test Signals

High-signal validation for this chunk includes:

- `jq empty sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-cache.json` succeeds on the full file.
- Full-file parsing reports 1,111 top-level event objects.
- A line-range scan of 5371-10335 finds 462 `EventName` fields, all with `Unit: "CHA"` in the visible records.
- Representative event families are present with expected selectors: `UNC_CHA_RxC_WBQ1_REJECT.*` at `0x29`, `UNC_CHA_RxR_INSERTS.*` at `0xE1`, `UNC_CHA_TOR_INSERTS.*` at `0x35`, `UNC_CHA_TOR_OCCUPANCY.*` at `0x36`, and horizontal TxR events at `0xA2`, `0xA3`, `0xA6`, and `0xA7`.
- Perf PMU event table generation for the x86 `icelakex` directory succeeds without schema errors.
- On matching Ice Lake Xeon hardware, `perf list` exposes representative events from this range.
- `perf stat -e` can schedule simple individual events such as `UNC_CHA_TOR_INSERTS.IA_MISS_DRD`, `UNC_CHA_TOR_OCCUPANCY.IA_MISS_DRD`, `UNC_CHA_SNOOPS_SENT.REMOTE`, and `UNC_CHA_TxR_HORZ_CYCLES_FULL.AD_ALL`.
- Hardware sanity tests show expected directionality: TOR insert counts rise under memory traffic, occupancy rises under sustained queue pressure, snoop events rise under coherence-heavy traffic, and horizontal TxR full/not-empty cycles rise under mesh egress pressure.

## Cross-Chunk Notes

This is a chunk-level artifact only. It should not be treated as the final per-file research document.

The preceding chunk is needed for the complete opening object around `UNC_CHA_RxC_WBQ1_REJECT.LLC_OR_SF_WAY` and the earlier part of the `uncore-cache.json` table. The following chunk is needed to complete `UNC_CHA_TxR_HORZ_CYCLES_NE.BL_ALL` and the remaining horizontal transmit-ring/cache event definitions after line 10335.
