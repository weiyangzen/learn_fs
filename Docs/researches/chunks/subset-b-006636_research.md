# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-interconnect.json lines 3889-4452

## Scope

This chunk covers the final 564 lines of the BroadwellX `uncore-interconnect.json` PMU event table. The range starts at the `UNC_S_RxR_BYPASS.BL_BNC` SBOX entry and runs through the closing `]` of the JSON array. It contains only static event records; there are no functions, conditionals, or local runtime state in this source file.

The chunk is source-tree-aligned with perf's PMU event database under `tools/perf/pmu-events/arch/x86/broadwellx`. These records become BroadwellX uncore aliases in generated `pmu-events.c` output, where perf can expose symbolic event names instead of requiring users to spell raw event and umask values.

## Purpose

The purpose of this tail chunk is to describe SBOX and UBOX interconnect monitoring events for Intel BroadwellX-class systems. These are package-scoped uncore events (`"PerPkg": "1"`) that perf can map onto uncore PMUs:

- `Unit: "SBOX"` maps to the generated PMU name `uncore_sbox`.
- `Unit: "UBOX"` maps to the generated PMU name `uncore_ubox`.

The covered SBOX entries describe ring ingress and egress behavior:

- SBOX ingress bypass tracking via `UNC_S_RxR_BYPASS.*` for BL bounce, BL credit, and IV traffic.
- SBOX ingress credit starvation via `UNC_S_RxR_CRD_STARVED.*` for AD bounce, AD credit, AK, BL bounce, BL credit, IFV, and IV traffic.
- SBOX ingress allocation counts via `UNC_S_RxR_INSERTS.*` for AD, AK, BL, and IV classes.
- SBOX ingress occupancy via `UNC_S_RxR_OCCUPANCY.*` for the same traffic classes.
- SBOX Tx ring address-slot usage via `UNC_S_TxR_ADS_USED.AD`, `.AK`, and `.BL`.
- SBOX egress allocations and occupancy via `UNC_S_TxR_INSERTS.*` and `UNC_S_TxR_OCCUPANCY.*`.
- SBOX egress starvation onto the AD, AK, BL, and IV rings via `UNC_S_TxR_STARVED.*`.

The covered UBOX entries describe package-level uncore box behavior:

- Fixed UBOX clockticks via `UNC_U_CLOCKTICKS`.
- Event-message receipt via `UNC_U_EVENT_MSG.DOORBELL_RCVD`.
- Thread-filter match events via `UNC_U_FILTER_MATCH.*`.
- PHOLD cycles via `UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK`.
- Outstanding RACU register requests via `UNC_U_RACU_REQUESTS`.
- UBOX-to-core monitor and error delivery via `UNC_U_U2C_EVENTS.*`.

## Data Model and Important Fields

Each item is a JSON object in the schema consumed by `tools/perf/pmu-events/jevents.py`. Important fields in this chunk are:

- `EventName`: Symbolic perf alias source. `jevents.py` lowercases this value, so `UNC_S_RxR_BYPASS.BL_BNC` becomes a generated event name like `unc_s_rxr_bypass.bl_bnc`.
- `EventCode`: Raw PMU event selector. SBOX entries in this chunk use selectors including `0x1`, `0x2`, `0x3`, `0x4`, `0x11`, `0x12`, `0x13`, and `0x14`; UBOX entries use `0x41`, `0x42`, `0x43`, `0x45`, `0x46`, and fixed `0xff`.
- `UMask`: Unit mask appended to the generated event string when present and non-zero. It differentiates the AD/AK/BL/IV traffic classes and UBOX subevents under a shared event selector.
- `Counter`: Legal counter set. SBOX events use counters `0,1,2,3`; most UBOX programmable events use `0,1`; `UNC_U_CLOCKTICKS` uses `FIXED`.
- `Unit`: Uncore block name used by `jevents.py` to derive the perf PMU name. Unknown/non-special units become `uncore_<unit-lowercase>`.
- `PerPkg`: Marks the event as package-scoped in generated `struct pmu_event.perpkg`.
- `BriefDescription`: Short description used as `struct pmu_event.desc`.
- `PublicDescription`: Longer help text used as `struct pmu_event.long_desc`. Some entries, such as `UNC_S_TxR_ADS_USED.*` and `UNC_U_CLOCKTICKS`, omit `PublicDescription`, making the brief description the main user-facing text.

No entry in this chunk defines metrics, formulas, PEBS precision, MSR filters, port masks, counter masks, or architecture-standard indirection. The generated event string is therefore mostly `event=<EventCode>,umask=<UMask>` plus PMU routing metadata.

## Event Families

### SBOX RxR Bypass and Starvation

Lines 3889-3917 finish the `UNC_S_RxR_BYPASS.*` family. The earlier AD and AK entries are owned by the previous chunk, while this chunk contributes BL bounce (`umask=0x8`), BL credit (`umask=0x4`), and IV (`umask=0x20`). These all share `EventCode 0x12` and describe traffic that bypasses the SBOX ingress queue.

Lines 3918-3987 define `UNC_S_RxR_CRD_STARVED.*`, all with `EventCode 0x14`. These count ingress starvation when an ingress entry cannot forward toward egress because credits are unavailable. The masks split the condition by ring/message class:

- AD credit: `0x1`.
- AD bounce: `0x2`.
- BL credit: `0x4`.
- BL bounce: `0x8`.
- AK: `0x10`.
- IV: `0x20`.
- IFV: `0x40`.

These events are useful when diagnosing ring pressure where ingress work is present but cannot make progress because the downstream path lacks credit.

### SBOX RxR Inserts and Occupancy

Lines 3988-4047 define `UNC_S_RxR_INSERTS.*` with `EventCode 0x13`. The family counts allocations into the SBOX ingress, which queues requests received from the ring. The covered masks are AD credit, AD bounce, AK, BL credit, BL bounce, and IV.

Lines 4048-4107 define `UNC_S_RxR_OCCUPANCY.*` with `EventCode 0x11`. These occupancy events accumulate how occupied the same ingress buffers are for each traffic class. The distinction between inserts and occupancy matters: inserts are event counts, while occupancy-style events are cycle-accumulated queue-depth signals and need interpretation against elapsed cycles or a clock event.

### SBOX TxR Address Use, Inserts, Occupancy, and Starvation

Lines 4108-4134 define `UNC_S_TxR_ADS_USED.AD`, `.AK`, and `.BL` with `EventCode 0x4` and masks `0x1`, `0x2`, and `0x4`. These records lack long descriptions, so downstream help output has less context than the surrounding SBOX families. Based on the names and placement, they monitor address-slot usage on Tx ring classes.

Lines 4135-4194 define `UNC_S_TxR_INSERTS.*` with `EventCode 0x2`. These count allocations into SBOX egress queues for requests destined for the ring.

Lines 4195-4254 define `UNC_S_TxR_OCCUPANCY.*` with `EventCode 0x1`. These mirror the egress side of the ingress occupancy family and describe how occupied egress buffers are for AD, AK, BL, and IV traffic classes.

Lines 4255-4294 define `UNC_S_TxR_STARVED.*` with `EventCode 0x3`. They count egress injection starvation when egress cannot send a transaction onto the AD, AK, BL, or IV ring for a long time. These are a direct signal for ring-side backpressure at the point of injection.

### UBOX Clock, Filter, PHOLD, RACU, and U2C Events

Lines 4295-4302 define `UNC_U_CLOCKTICKS`, a fixed-counter UBOX clocktick event with `EventCode 0xff`. It is the natural denominator for UBOX rates and occupancy-like interpretations.

Lines 4303-4312 define `UNC_U_EVENT_MSG.DOORBELL_RCVD`, which counts received Virtual Logical Wire legacy messages. Its long description states that filtering uses `NCUPMONCTRLGLCTR.ThreadID`; this register-level filter is not encoded as a JSON `Filter` field, so consumers need platform knowledge or perf syntax support outside this record.

Lines 4313-4352 define `UNC_U_FILTER_MATCH.*` variants with `EventCode 0x41`: `ENABLE`, `DISABLE`, `U2C_ENABLE`, and `U2C_DISABLE`. They describe per-thread filter matches with or without filter enablement, again referring to `NCUPMONCTRLGLCTR.ThreadID`.

Lines 4353-4362 define `UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK`, a PHOLD cycle counter with a source CoreID filter mentioned in text.

Lines 4363-4371 define `UNC_U_RACU_REQUESTS`, which counts outstanding register requests within the message-channel tracker.

Lines 4372-4451 define `UNC_U_U2C_EVENTS.*` with `EventCode 0x43`. The masks split monitor/error events delivered from uncore toward cores:

- `MONITOR_T0`: `0x1`.
- `MONITOR_T1`: `0x2`.
- `LIVELOCK`: `0x4`.
- `LTERROR`: `0x8`.
- `CMC`: `0x10`.
- `UMC`: `0x20`.
- `TRAP`: `0x40`.
- `OTHER`: `0x80`, described as PREQ, PSMI, P2U, Thermal, PCUSMI, and PMI.

## Control Flow and Integration

This JSON file has no direct control flow. Its integration path is build-time and runtime data plumbing:

1. `tools/perf/pmu-events/README` defines the PMU event database layout: architecture model directories contain topic JSON files, and `jevents` processes them before perf itself is built.
2. `tools/perf/pmu-events/jevents.py` reads JSON arrays with `json.load(..., object_hook=JsonEvent)`.
3. `JsonEvent.__init__()` maps fields from each object into generated event attributes. For this chunk, `EventName` becomes lowercase `name`, `BriefDescription` becomes `desc`, `PublicDescription` becomes `long_desc`, `Unit` becomes an uncore PMU name, `PerPkg` becomes package aggregation metadata, `EventCode` becomes `event=<value>`, and non-zero `UMask` becomes `umask=<value>`.
4. `JsonEvent.to_c_string()` serializes the parsed event into generated compact C string-table data for `pmu-events.c`.
5. At perf runtime, APIs declared in `tools/perf/pmu-events/pmu-events.h` expose the generated tables through `perf_pmu__find_events_table()`, `pmu_events_table__for_each_event()`, `pmu_events_table__find_event()`, and `pmu_events_table__num_events()`.
6. User commands such as `perf list` and `perf stat -e <event>` can then discover or resolve aliases for the matching BroadwellX uncore PMUs.

The mapfile for x86 selects model directories such as `broadwellx`; this file's events are part of that model's uncore interconnect topic rather than the core CPU event table.

## State and Persistence

There is no mutable software state in the chunk. The persistent contract is the static mapping from symbolic names to hardware PMU event selectors and masks.

The important persisted semantics are:

- The SBOX/UBOX hardware selector and mask values are treated as authoritative for BroadwellX uncore PMU programming.
- `PerPkg` tells perf these are package-level uncore events, which affects aggregation and alias display.
- `Counter` limits which hardware counters can count an event, but the JSON-to-`pmu_event` conversion primarily carries this as event metadata for the generated table and help text path rather than implementing scheduling logic in this file.
- Description strings persist into generated help output and into programmatic event listings.

Because this is source data, any incorrect event code, mask, unit, or name persists into all generated perf binaries built from this tree.

## Dependencies

The chunk depends on:

- The perf PMU event JSON schema recognized by `jevents.py`.
- Python JSON parsing during the `jevents` build step.
- The BroadwellX x86 mapfile entries that route this model to the `broadwellx` directory.
- Linux perf uncore PMU names matching generated unit names such as `uncore_sbox` and `uncore_ubox`.
- The kernel's uncore PMU drivers exposing compatible SBOX and UBOX PMUs and accepting the event/umask encodings listed here.
- Runtime lookup helpers declared in `pmu-events.h` and used by perf list/stat tooling.

There are no local includes or code-level APIs in the JSON itself, but the field names are an API between the static data and the generator.

## Risks

- The chunk begins in the middle of the complete `UNC_S_RxR_BYPASS.*` family. A whole-file report must reconcile the AD and AK bypass records from the previous chunk with the BL/IV records here.
- `EventCode`/`UMask` errors are hard failures in practice: perf may still create an alias, but it would program the wrong hardware counter and produce misleading performance data.
- `Unit` is semantically important. A typo would route an event to the wrong generated PMU name, likely making aliases invisible or unusable for the real BroadwellX uncore device.
- Several descriptions contain hardware-register filtering guidance, such as `NCUPMONCTRLGLCTR.ThreadID` and source CoreID filters, but the JSON records do not encode those filters in machine-readable `Filter` fields. Users may see the event but still need separate knowledge to apply thread/core filtering correctly.
- `UNC_S_TxR_ADS_USED.*` records have only terse brief descriptions and no `PublicDescription`, increasing the chance of user confusion and reducing generated documentation quality.
- Occupancy events and insertion events share similar traffic-class naming but have different interpretation. Treating occupancy as a simple transaction count can lead to wrong conclusions.
- Counter constraints differ between SBOX, UBOX programmable counters, and the UBOX fixed counter. Alias availability may depend on perf scheduling and the physical PMU counter layout.
- The final `]` closes the entire JSON array. Any edit near this chunk can break parsing for the whole BroadwellX interconnect topic.

## Test and Validation Signals

Useful validation signals for this chunk are:

- Run the perf PMU event generation path and ensure `jevents.py` parses `arch/x86/broadwellx/uncore-interconnect.json` without JSON exceptions.
- Validate the generated event strings for sample aliases. Examples should include `UNC_S_RxR_CRD_STARVED.IFV` producing `event=0x14,umask=0x40`, `UNC_S_TxR_STARVED.IV` producing `event=0x3,umask=0x8`, and `UNC_U_U2C_EVENTS.OTHER` producing `event=0x43,umask=0x80`.
- Build perf and run PMU event tests, especially the tests under `tools/perf/tests/pmu-events.c` that compare generated tables and event lookup behavior.
- Use `perf list` on a BroadwellX-capable environment, or with generated table inspection in a build tree, to confirm the SBOX and UBOX aliases appear under the expected uncore PMUs.
- On real hardware, run low-impact `perf stat -a -e` checks against representative aliases such as `unc_s_rxr_inserts.iv`, `unc_s_txr_starved.ad`, and `unc_u_clockticks` to verify event resolution and counter scheduling.
- For documentation quality, inspect `perf list --details` output for entries without `PublicDescription`, especially `UNC_S_TxR_ADS_USED.*`, to make sure terse descriptions are still acceptable.
