# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-cache.json lines 1-5335

## Scope

This chunk covers the first 5,335 lines of the Sapphire Rapids `uncore-cache.json` PMU event table. The source file is a large top-level JSON array consumed by perf's PMU event generation path; this chunk starts at the opening `[` and stops in the middle of the `UNC_CHA_TOR_INSERTS.PMM` object, so the final object and the remainder of the file must be reconciled by later chunks before any whole-file conclusions are made.

## Purpose

The chunk defines symbolic uncore cache events for Intel Sapphire Rapids, almost entirely for the CHA PMU (`"Unit": "CHA"`). These definitions let perf users request named events instead of raw event/select encodings, and they give `perf list`/Python bindings enough metadata to expose short and long descriptions.

Important event families visible here include:

- `UNC_CHA_BYPASS_CHA_IMC`, `UNC_CHA_IMC_READS_COUNT`, `UNC_CHA_IMC_WRITES_COUNT`, and `UNC_CHA_READ_NO_CREDITS` for CHA-to-memory-controller behavior.
- `UNC_CHA_CORE_SNP`, `UNC_CHA_SNOOPS_SENT`, `UNC_CHA_SNOOP_RESP`, `UNC_CHA_SNOOP_RESP_LOCAL`, and `UNC_CHA_SNOOP_RSP_MISC` for snoop issuance and response classification.
- `UNC_CHA_DIR_LOOKUP`, `UNC_CHA_DIR_UPDATE`, `UNC_CHA_HITME_*`, and `UNC_CHA_OSB` for directory, HitME, and opportunistic snoop broadcast behavior.
- `UNC_CHA_LLC_LOOKUP`, `UNC_CHA_LLC_VICTIMS`, `UNC_CHA_MISC`, and `UNC_CHA_REQUESTS` for LLC/snoop-filter lookup, victimization, miscellaneous cache events, and local/remote read/write requests.
- `UNC_CHA_RxC_*` for ingress allocations, occupancy, reject, and retry reasons across IPQ, IRQ, ISMQ, PRQ, RRQ, WBQ, and aggregate request queues.
- `UNC_CHA_PMM_*` for persistent-memory/near-memory mode and QoS-related signals.
- `UNC_CHA_TOR_INSERTS`, the largest family in this chunk, for TOR insertion classification by source, opcode, hit/miss state, local/remote target, DDR/PMM/CXL target, and IA/IO origin.

## Data Schema and Important Fields

Each array entry is a PMU event object. The primary fields in this chunk are:

- `EventName`: public symbolic name, usually uppercase with a family/subevent split such as `UNC_CHA_LLC_LOOKUP.DATA_RD`.
- `EventCode`: raw event selector, commonly shared across a family, for example `0x34` for LLC lookups, `0x35` for TOR inserts, `0x37` for LLC victims, and `0x5c`/`0x5d` for snoop responses.
- `UMask`: unit mask or extended mask. Simple families use small masks such as `0x1`, while TOR insert filters use wide extended encodings such as `0xc817fe01` and CXL-related masks such as `0x10c8178201`.
- `Counter`: allowed counter indexes. Most events allow `0,1,2,3`; occupancy events such as `UNC_CHA_RxC_OCCUPANCY.*` are restricted to counter `0`.
- `Unit`: `CHA`, mapped by `jevents.py` to the runtime uncore PMU name form `uncore_cha`.
- `PerPkg`: most entries carry `"1"`, so callers should treat counts as package-level uncore events rather than per-core events.
- `Experimental`: many events are marked `"1"`, which signals lower stability or less-public validation.
- `BriefDescription` and `PublicDescription`: text shown by perf tooling. Some events have only a brief description, and some descriptions are generic or copied across related events.
- `PortMask`: appears on several CXL accelerator local filters with `"0x000"`. Because `jevents.py` suppresses zero-valued fields, this does not emit a `ch_mask=` term but still documents intended locality.

The JSON schema is data-only. It defines no C/Python functions itself, but its fields are interpreted by `tools/perf/pmu-events/jevents.py`, particularly `JsonEvent`, which lowercases `EventName`, canonicalizes hexadecimal fields, maps `Unit` to PMU names, and builds perf event strings such as `event=0x35,umask=0xc817fe01`.

## Integration Points

The file participates in the standard perf PMU-event pipeline:

- `tools/perf/pmu-events/Build` drives `jevents.py` over `pmu-events/arch`.
- `jevents.py` traverses model JSON files, reads event objects, and emits generated `pmu-events.c`.
- `pmu-events/README` describes the contract: JSON files in model/topic directories become generated PMU tables, model mapping comes from `mapfile.csv`, and perf selects the right table at runtime from CPU identification.
- `util/pmu.c`, `util/pmu.h`, `builtin-list.c`, `util/python.c`, and `tools/perf/python/ilist.py` consume generated event metadata for alias resolution, listing, and Python export.
- `tests/pmu-events.c`, `tests/parse-metric.c`, and shell tests provide generated-table and parse validation signals.

The source path places the file under `arch/x86/sapphirerapids`, so the table is selected only for matching x86 Sapphire Rapids CPU mappings rather than for all architectures.

## Control Flow

There is no runtime control flow in this JSON file. The relevant flow is build-time and lookup-time:

1. The perf build system invokes `jevents.py` unless `NO_JEVENTS=1` is set.
2. `jevents.py` walks JSON files, including this cache-topic file.
3. For each event object, it constructs a generated table row. `EventCode` becomes `event=...`; nonzero `UMask`, `PortMask`, `CounterMask`, and related fields become comma-separated config terms.
4. Generated `pmu-events.c` is compiled into libperf/perf.
5. At runtime, perf matches CPU identity to the Sapphire Rapids table and exposes aliases such as `unc_cha_llc_lookup.data_rd` through perf event parsing and `perf list`.

Within this chunk, the data is organized as contiguous families. Consumers do not branch on the family layout directly, but the shared `EventCode`/varying `UMask` pattern is how related aliases map to the same PMU event selector with different filters.

## State and Persistence Behavior

The source file is static metadata persisted in the repository. It has no mutable state, no runtime persistence, and no side effects. Its practical persisted outputs are generated build artifacts:

- `pmu-events.c`, produced from this and other JSON files.
- Object/library artifacts such as `pmu-events.o` and `libpmu-events.a`.
- User-visible event aliases and descriptions embedded in the perf binary.

Changes to any event name, code, mask, or description alter generated output and can break scripts that rely on exact symbolic names or raw config encodings.

## Dependencies and Assumptions

This chunk depends on perf's PMU JSON conventions and the parser behavior in `jevents.py`:

- Field names are case-sensitive and expected by tooling.
- `EventName` is lowercased in generated data, so names must remain unique after lowercasing.
- `EventCode` and masks must parse as integer strings accepted by Python `int(..., 0)`.
- Zero-valued filter fields are intentionally skipped by `jevents.py`.
- Missing `UMask` is valid for some aliases, but it means the generated config only carries the base event unless additional parser-side filters are supplied.

Hardware assumptions are embedded in the descriptions and masks: CHA events are Sapphire Rapids-specific, many counters are package-level, and some TOR insert masks distinguish IA/IO, local/remote, DDR/PMM, and CXL accelerator traffic.

## Risks and Edge Cases

- The chunk boundary cuts through the `UNC_CHA_TOR_INSERTS.PMM` object; the next chunk must complete that object and preserve JSON validity during merge research.
- Many `UNC_CHA_LLC_LOOKUP.*` and `UNC_CHA_TOR_INSERTS.*` aliases intentionally omit `UMask`. If a consumer expects every event alias to include `umask=`, these entries can appear under-specified even though perf may rely on additional filters or generic event behavior.
- Extended `UMask` values exceed the width of simple 8-bit masks. Any downstream truncation or schema assumption that treats `UMask` as byte-sized would corrupt TOR/CXL filters.
- Repeated descriptions are common. Some entries have descriptions that are generic, incomplete, or appear copied from related events; for example several writeback TOR insert events mention `WbEFtoE` even when the `EventName` indicates `WBMTOE`, `WBMTOI`, or `WBSTOI`.
- Local/remote wording should be validated carefully. In this chunk, `UNC_CHA_TOR_INSERTS.IO_PCIRDCUR_LOCAL` and `.REMOTE` descriptions appear textually swapped relative to their suffixes.
- `ANY0` aggregate descriptions in the RxC retry/reject families are repetitive and may reference a sibling queue family due to copy/paste. The masks are likely the authoritative contract.
- `PortMask: "0x000"` is present for some CXL-local aliases but is suppressed as zero by `jevents.py`; if the value was intended to force a mask rather than document it, generated event strings will not contain it.
- Most events are marked `Experimental`, so stable user-facing metrics should avoid assuming the semantics are frozen.
- Because `PerPkg` is set on nearly every event, aggregation behavior across sockets/packages can be misunderstood if callers compare results to per-core events.

## Test and Validation Signals

Useful checks for this chunk are:

- JSON validity of the full file after all chunks are considered; this chunk alone is not valid JSON because it ends mid-object.
- Build-time `jevents.py` generation through `tools/perf/pmu-events/Build`, ensuring every event object parses and emits generated C.
- `make JEVENTS_ARCH=all` or a Sapphire Rapids-targeted perf build to catch malformed masks, duplicate generated names, and invalid event fields.
- `tools/perf/tests/pmu-events.c` to compare generated event tables against expected parser behavior.
- `perf list --details` on a Sapphire Rapids-capable build to confirm representative aliases are visible with expected `event=`/`umask=` strings.
- Targeted spot checks for the dominant families: `UNC_CHA_LLC_LOOKUP.DATA_RD`, `UNC_CHA_REQUESTS.READS_LOCAL`, `UNC_CHA_RxC_IPQ0_REJECT.AD_REQ_VN0`, `UNC_CHA_SNOOP_RESP.RSPIFWD`, and several `UNC_CHA_TOR_INSERTS.IA_MISS_*` aliases with extended masks.
- Schema linting for duplicate `EventName`, invalid hex strings, missing required `EventCode`, and unintended missing `UMask` in families where masks should be explicit.

## Chunk-Specific Summary

Lines 1-5335 define the beginning and bulk of the CHA cache/uncore event catalog for Sapphire Rapids. The central technical content is a set of event-family aliases sharing event selectors and varying masks, especially LLC lookup state/request filters, queue reject/retry reasons, snoop response filters, and a large TOR insert taxonomy. The highest-risk integration points are correct interpretation of extended masks, missing masks on filter-style aliases, package-level aggregation, and textual consistency in descriptions. The remaining source lines are required to complete the current TOR insert family and produce a valid whole-file research document.
