# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-cache.json lines 1-5272

## Scope

This chunk covers the first 5,272 lines of `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-cache.json`, a Linux `perf` PMU event metadata table for Snow Ridge X x86 uncore cache/home-agent events. The file is JSON data, not executable code: its exported interface is the event record schema consumed by the perf PMU event tooling and by users selecting named uncore events. The full file has 8,543 lines; this chunk ends in the middle of the `UNC_CHA_TOR_INSERTS.IA_MISS_CRD_PREF` record, so the merge lane must combine it with the following chunk before treating the JSON array as syntactically complete.

## Purpose

The chunk defines 490 `UNC_CHA_*` event names for the `CHA` unit. These records describe how perf should map human-readable event names to uncore hardware selectors for cache/home-agent monitoring: `EventCode`, optional `UMask`, counter availability, package scope, descriptions, and compatibility flags. Most events are marked `Experimental`, a few are `Deprecated`, and almost all are package-scoped via `PerPkg`.

The data is organized as a long array of event objects. Each object is one perf event variant or subevent. The `EventName` prefix groups related measurements, while the suffix after `.` names a subfilter such as traffic class, coherence state, ring direction, retry reason, hit/miss qualifier, or transgress selector.

## Schema And API Surface

Important fields in this chunk:

- `EventName`: primary public API. Perf users and higher-level metric tooling refer to strings such as `UNC_CHA_LLC_LOOKUP.READ_MISS`, `UNC_CHA_RxC_ISMQ0_RETRY.AD_REQ_VN0`, or `UNC_CHA_TOR_INSERTS.IA_HIT_RFO`.
- `EventCode`: raw hardware event selector. Many event families share one code and differentiate subevents through `UMask`.
- `UMask`: subevent bitmask or encoded filter. Simple families use powers of two; lookup/TOR families use wider composite masks such as `0xc001ffff`.
- `Counter`: allowed CHA counters. In this chunk, 489 records use `0,1,2,3`; `UNC_CHA_RxC_OCCUPANCY.IRQ` is counter `0` only.
- `Unit`: always `CHA` in this chunk, binding records to the CHA uncore PMU rather than core PMUs or memory-controller PMUs.
- `PerPkg`: almost always `1`, indicating package-scoped aggregation/availability.
- `BriefDescription` and `PublicDescription`: user-visible descriptions surfaced by perf event listing and documentation generation. `PublicDescription` often contains critical caveats that are not inferable from the event name.
- `Experimental`: present on 464 records, signaling event stability or documentation confidence risk.
- `Deprecated`: present on 7 records, redirecting old names to newer aliases.

There are no functions or types in the source file. The implicit type is a perf PMU JSON event object, and the main compatibility contract is field spelling plus valid JSON array syntax.

## Event Families In This Chunk

The opening section defines CMS agent credit acquisition and occupancy events for agent 0/1, AD/BL channels, and transgress selectors 0-10. These include families such as `UNC_CHA_AG0_AD_CRD_ACQUIRED0`, `UNC_CHA_AG0_AD_CRD_OCCUPANCY0`, `UNC_CHA_AG1_BL_CRD_ACQUIRED1`, and related variants. They all target `CHA`, use counters `0,1,2,3`, and encode transgresses through `UMask` bits.

The next major group covers CHA bypass, clock, snoop, direct-GO, distress, egress, and ring-use behavior. Examples include `UNC_CHA_BYPASS_CHA_IMC`, `UNC_CHA_CLOCKTICKS`, `UNC_CHA_CMS_CLOCKTICKS`, `UNC_CHA_CORE_SNP`, `UNC_CHA_DIRECT_GO`, `UNC_CHA_DIRECT_GO_OPC`, `UNC_CHA_DISTRESS_ASSERTED`, `UNC_CHA_EGRESS_ORDERING`, and horizontal ring-use families for AD, AK, AKC, BL, and IV. Public descriptions for the ring events explain left/right, even/odd, clockwise/counter-clockwise behavior, which matters when interpreting per-CHA tile counts.

The LLC and snoop-filter region is centered on `UNC_CHA_LLC_LOOKUP`, the largest family in this chunk with 41 variants. It includes request classes, hit/miss variants, MESI/F-state selectors, local/remote home qualifiers, and deprecated aliases. The descriptions warn that lookup filtering is nonstandard: state bits must be selected or the event may count nothing, and some requests may increment multiple times if they perform multiple lookups. Related families include `UNC_CHA_LLC_VICTIMS`, `UNC_CHA_SF_EVICTION`, `UNC_CHA_SNOOPS_SENT`, `UNC_CHA_SNOOP_RESP_LOCAL`, and `UNC_CHA_SNOOP_RSP_MISC`.

Memory-controller-facing CHA traffic is represented by `UNC_CHA_IMC_READS_COUNT` and `UNC_CHA_IMC_WRITES_COUNT`, covering normal/priority reads and full/partial writes. These are still CHA-unit events even though the descriptions mention iMC/HA paths.

Request, retry, reject, and queue pressure families dominate the middle of the chunk. They include `UNC_CHA_PIPE_REJECT`, `UNC_CHA_READ_NO_CREDITS`, `UNC_CHA_REQUESTS`, `UNC_CHA_MISC`, `UNC_CHA_MISC_EXTERNAL`, `UNC_CHA_RxC_INSERTS`, `UNC_CHA_RxC_IRQ*_REJECT`, `UNC_CHA_RxC_ISMQ*_REJECT`, `UNC_CHA_RxC_ISMQ*_RETRY`, `UNC_CHA_RxC_OTHER*_RETRY`, `UNC_CHA_RxC_PRQ*_REJECT`, `UNC_CHA_RxC_REQ_Q*_RETRY`, and `UNC_CHA_RxC_OCCUPANCY`. These records expose reasons such as no AD/BL VN0 credit, non-UPI AK/IV injection failure, LLC/SF way conflicts, victims, physical-address matches, and allow-snoop gating.

Ring and response-router telemetry appears in `UNC_CHA_RING_BOUNCES_HORZ`, `UNC_CHA_RING_BOUNCES_VERT`, `UNC_CHA_RING_SINK_STARVED_HORZ`, `UNC_CHA_RING_SINK_STARVED_VERT`, `UNC_CHA_RING_SRC_THRTL`, and `UNC_CHA_RxR_*` families. `RxR` variants distinguish occupancy, inserts, bypass, busy starvation, and credit starvation across AD, BL, AK, AKC, and IV traffic classes.

The final visible section begins `UNC_CHA_TOR_INSERTS`, with 24 variants present before the chunk boundary. It defines TOR insertion counts for all requests, DDR, evictions, hits, IA-originated requests, CLFLUSH/CLFLUSHOPT, CRD/DRD/RFO types, hit/miss qualifiers, and page-walk PTE reads. The chunk stops after the `EventName` and `PerPkg` lines for `UNC_CHA_TOR_INSERTS.IA_MISS_CRD_PREF`; its `PublicDescription`, `UMask`, `Unit`, closing object, and following entries are outside this chunk.

## Control Flow And Consumption

Runtime control flow is external to this JSON file. Perf's PMU event build/listing path reads architecture/model JSON files, validates/parses each object, generates event tables or lookup data, and later resolves user-facing event names into raw event selectors. For any one event in this chunk, the effective flow is:

1. Select the Snow Ridge X PMU event map.
2. Match a user-supplied event name to `EventName`.
3. Bind the event to the `CHA` PMU because `Unit` is `CHA`.
4. Program one of the listed counters using `EventCode` plus `UMask` when present.
5. Apply package scope and report descriptions/flags in listing/help output.

The file itself has no branches, loops, runtime mutation, or persistence. Its order is nevertheless significant for reviewability and generated table determinism, and duplicate/deprecated aliases may intentionally coexist for compatibility.

## State And Persistence

The JSON records are static source-controlled state. They persist hardware event knowledge in the repository and are transformed by perf tooling into compiled metadata or installed event map files. There is no runtime state stored by this file, but downstream behavior depends on stable event names, masks, and descriptions. Renaming, deleting, or changing masks is a compatibility-impacting data change for scripts, dashboards, and tests that reference these event names.

Deprecated records preserve old public names while steering users to newer event names. Experimental flags preserve uncertainty/stability metadata and should not be stripped mechanically.

## Dependencies And Integration Points

Primary dependencies are the Linux perf PMU event JSON schema and the perf parser/generator that expects exact field names such as `BriefDescription`, `EventCode`, `EventName`, `UMask`, `Unit`, `Counter`, `PerPkg`, `Experimental`, and `Deprecated`. The source path places this data under `tools/perf/pmu-events/arch/x86/snowridgex`, so it integrates with the x86 Snow Ridge X model mapping rather than with Ceph runtime code despite living under the repository's `sources/distributed-fs/ceph-client` mirror.

Integration points include:

- `perf list` and generated event documentation, which expose names/descriptions.
- `perf stat` or similar event selection paths, which rely on event names resolving to valid raw CHA selectors.
- PMU event table generation tests that parse all JSON files and reject malformed arrays, invalid fields, or duplicate unintended names.
- Architecture model mapping files that decide when Snow Ridge X events are available.

## Risks And Edge Cases

The largest risk in this chunk is data correctness rather than algorithmic behavior. Incorrect `EventCode` or `UMask` values silently measure the wrong hardware condition. This risk is especially high for composite masks in `UNC_CHA_LLC_LOOKUP` and `UNC_CHA_TOR_INSERTS`, where many variants differ by small encoded bit changes.

Several `UNC_CHA_LLC_LOOKUP` descriptions require specific state/filter selections. If users or derived metrics compose these events without the required state bits, they can observe zero counts or misleading counts. The event may also count multiple increments for requests that perform multiple lookups, so it is not necessarily a one-request-one-count metric.

The 7 deprecated records are intentional compatibility aliases. Removing them may break old perf command lines; keeping them without clear replacement text may confuse users. This chunk includes deprecated LLC lookup aliases such as `CODE`, `DATA_RD`, `DATA_READ_ALL`, `DMND_READ_LOCAL`, `RFO_PREF_LOCAL`, and `WRITE_LOCAL`, plus `UNC_CHA_TOR_INSERTS.DDR4` pointing to `UNC_CHA_TOR_INSERTS.DDR`.

The chunk boundary is inside an object, so line-limited processing cannot parse this chunk alone as standalone JSON. Any validator for this chunk must either parse the complete source file or understand that this is a partial chunk artifact.

Nearly every record is package-scoped and counter `0,1,2,3`, but `UNC_CHA_RxC_OCCUPANCY.IRQ` is counter `0` only. Tooling that assumes all CHA events can use all four counters would mishandle this event.

Some descriptions contain legacy or platform-specific wording such as CBo, JKT, HA, CMS, ISMQ, PRQ, IRQ, TOR, and VN0. These are domain terms rather than local code identifiers; cleanup that rewrites descriptions for style could remove necessary hardware semantics.

## Test Signals

Useful validation signals for this chunk and the eventual merged file:

- The complete `uncore-cache.json` must parse as one valid JSON array; this chunk alone should not be required to parse independently because it ends mid-record.
- Every complete record in this chunk should have `EventName` and `Unit`, and `Unit` should remain `CHA`.
- Event names should remain unique unless perf intentionally permits aliases through deprecated records.
- `Deprecated` records should include replacement guidance in `BriefDescription` where available.
- `Counter` values should be checked against PMU capabilities; at minimum preserve the `Counter: "0"` special case for `UNC_CHA_RxC_OCCUPANCY.IRQ`.
- Composite `UMask` values in LLC lookup and TOR insertion families should be compared against authoritative vendor data or neighboring architecture files before modification.
- Perf-side generation tests should cover listing representative events from each major family: credit occupancy, LLC lookup, IMC reads/writes, RxC retry/reject, RxR occupancy/inserts, snoop responses, and TOR inserts.
