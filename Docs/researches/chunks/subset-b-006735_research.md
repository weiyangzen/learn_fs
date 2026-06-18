# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-interconnect.json lines 6248-7419

## Scope And Purpose

This chunk is the tail of the Snow Ridge X x86 uncore interconnect PMU event map used by Linux `perf`. The source is a JSON array of event descriptors, not executable code. Its purpose is to describe hardware performance-monitoring aliases that `perf` can expose for the Snow Ridge uncore interconnect blocks, especially M2M and UBOX units.

The selected line range starts inside the `UNC_M2M_TxR_VERT_INSERTS0.BL_AG0` object and continues through the final closing array bracket. Interpreting the chunk by complete JSON objects, it covers 112 event descriptors: 86 `M2M` events and 26 `UBOX` events. All entries are package-scoped with `PerPkg: "1"`. Most are marked `Experimental: "1"`; the only non-experimental entry in this tail is the fixed UBOX clocktick event.

This data is source-tree-aligned with the perf PMU event database under `tools/perf/pmu-events/arch/x86/snowridgex`. It exists so the perf event-table generator and runtime event lookup can translate user-facing event names such as `UNC_M2M_VERT_RING_AD_IN_USE.UP_EVEN` into raw uncore PMU encodings.

## Data Schema And Important Fields

Each object is a PMU event descriptor consumed by perf's PMU-events tooling. The important fields in this chunk are:

- `EventName`: the stable perf alias. Names use dotted suffixes to identify ring, channel, agent, direction, or message subtype.
- `Unit`: the uncore PMU block. This chunk uses `M2M` for mesh-to-memory/interconnect events and `UBOX` for system-agent/uncore box events.
- `EventCode`: the raw event selector programmed into the unit PMU.
- `UMask`: the unit mask selecting a subtype within an event code. A few events, such as `UNC_U_CLOCKTICKS`, `UNC_U_LOCK_CYCLES`, and `UNC_U_RACU_REQUESTS`, do not specify a mask.
- `Counter`: the counter set that can count the event. M2M events use programmable counters `0,1,2,3`; UBOX events mostly use `0,1`; `UNC_U_CLOCKTICKS` uses the dedicated `FIXED` counter.
- `PerPkg`: all entries are package-level events, so consumers should aggregate or display them per socket/package rather than per core.
- `Experimental`: marks events whose semantics or availability may be less stable.
- `BriefDescription` and `PublicDescription`: user-facing text for `perf list` and generated documentation. Some entries only have a brief description.

There are no local functions, classes, or exported APIs in the file. The contract is the field names, valid JSON syntax, and consistency between the alias naming scheme and the raw hardware encodings.

## Event Families Covered

The M2M portion starts with vertical common-mesh-stop egress metrics:

- `UNC_M2M_TxR_VERT_INSERTS0` and `UNC_M2M_TxR_VERT_INSERTS1` count allocations into the CMS vertical egress for BL, IV, and AKC paths. The chunk includes BL agent 0/1, IV agent 0, and AKC agent 0/1 variants.
- `UNC_M2M_TxR_VERT_NACK0` and `UNC_M2M_TxR_VERT_NACK1` count vertical egress packets NACKed onto the vertical ring for AD, AK, BL, IV, and AKC paths.
- `UNC_M2M_TxR_VERT_OCCUPANCY0` and `UNC_M2M_TxR_VERT_OCCUPANCY1` count occupancy cycles for the CMS egress buffers feeding the vertical ring.
- `UNC_M2M_TxR_VERT_STARVED0` and `UNC_M2M_TxR_VERT_STARVED1` count injection starvation when the CMS egress cannot send a transaction onto the vertical ring for a long period.

The next M2M group measures vertical ring utilization:

- `UNC_M2M_VERT_RING_AD_IN_USE`, `AK_IN_USE`, `AKC_IN_USE`, `BL_IN_USE`, and `TGC_IN_USE` each provide up/down and even/odd variants where supported.
- `UNC_M2M_VERT_RING_IV_IN_USE` has only `UP` and `DN` variants.
- Public descriptions explain that the counted cycles include packets passing by or being sunk at the ring stop, but exclude packets sent from the ring stop. They also document the clockwise/counter-clockwise interpretation and the left-side/right-side reversal across CBo halves.

The final M2M group covers write path and M2M-to-iMC backpressure:

- `UNC_M2M_WPQ_FLUSH.CH0/CH1` count write-pending-queue flushes.
- `UNC_M2M_WPQ_NO_REG_CRD.CHN0/1/2` and `UNC_M2M_WPQ_NO_SPEC_CRD.CHN0/1/2` count M2M-to-iMC WPQ cycles without regular or special credits.
- `UNC_M2M_WR_TRACKER_FULL`, `WR_TRACKER_NE`, and `WR_TRACKER_OCCUPANCY` expose full, non-empty, and occupancy states for channel and mirror tracker variants.
- `UNC_M2M_WR_TRACKER_INSERTS`, `WR_TRACKER_POSTED_INSERTS`, `WR_TRACKER_NONPOSTED_INSERTS`, `WR_TRACKER_POSTED_OCCUPANCY`, and `WR_TRACKER_NONPOSTED_OCCUPANCY` distinguish insertion and occupancy behavior for posted versus non-posted write tracker traffic.

The UBOX tail describes system-agent events:

- `UNC_U_CLOCKTICKS` counts UBOX clockticks using a dedicated 48-bit fixed counter.
- `UNC_U_EVENT_MSG` variants count received doorbell, interrupt, IPI, MSI, and virtual logical wire messages.
- `UNC_U_LOCK_CYCLES` counts IDI lock/split-lock sequences.
- `UNC_U_M2U_MISC1`, `UNC_U_M2U_MISC2`, and `UNC_U_M2U_MISC3` cover receive/transmit channel fullness, emptiness, and credit-overflow signals between mesh and UBOX paths.
- `UNC_U_PHOLD_CYCLES.ASSERT_TO_ACK` counts PHOLD assert-to-ack cycles.
- `UNC_U_RACU_DRNG` variants count random-number-generation related activity (`RDRAND`, `RDSEED`, and prefetch-buffer-empty).
- `UNC_U_RACU_REQUESTS` counts outstanding RACU register requests within the message-channel tracker.

## Control Flow And Integration

This JSON has no runtime control flow by itself. The effective flow is data ingestion:

1. Perf build tooling reads architecture-specific JSON event files under `tools/perf/pmu-events/arch/x86`.
2. The PMU-events generator validates and converts these objects into generated event tables.
3. At runtime, perf matches the current CPU model to the Snow Ridge X event table.
4. Commands such as `perf list` display aliases and descriptions, while counting commands resolve `EventName` to the target uncore `Unit`, `EventCode`, `UMask`, package scope, and counter constraints.

The chunk's integration boundary is therefore schema compatibility with perf's PMU-events parser and semantic compatibility with the kernel uncore PMU driver for Snow Ridge. The `Unit` values must match perf's expected PMU naming for exposed uncore devices, and the `Counter` constraints must match hardware capabilities.

## State And Persistence Behavior

The file is static repository data. It does not persist runtime state, allocate resources, or mutate any store. Its persistent behavior is indirect: once built into perf's generated event tables, these descriptors become part of the installed perf binary or its generated PMU event metadata.

The counted hardware state is package-level uncore activity. M2M counters observe mesh/ring/write-tracker behavior across the package, while UBOX counters observe package-level message, lock, M2U, PHOLD, DRNG, and RACU activity. Because these are uncore counters, test and operational interpretation should account for socket/package topology and avoid assuming per-thread or per-core attribution.

## Dependencies And External Contracts

The main dependencies are:

- Perf's JSON PMU event schema and generator, including support for `BriefDescription`, `PublicDescription`, `Counter`, `EventCode`, `EventName`, `Experimental`, `PerPkg`, `UMask`, and `Unit`.
- Snow Ridge X uncore PMU hardware encodings for M2M and UBOX blocks.
- Linux perf runtime lookup for architecture/model-specific event aliases.
- Kernel uncore PMU devices exposing compatible `M2M` and `UBOX` units and counter ranges.

The file also depends on consistency with adjacent entries in the same JSON file. The line range starts after earlier M2M vertical insertion variants and continues to the end of the array, so merge/reconciliation should preserve the fact that this is one continuous JSON array rather than an independent document fragment.

## Risks And Edge Cases

The largest correctness risk is silent metadata drift. Wrong `EventCode` or `UMask` values would still parse as valid JSON but count a different hardware signal. Wrong `Unit` or `Counter` values can make aliases unavailable, fail at event open time, or schedule onto unsupported counters.

Alias consistency is also important. Most families encode subtype information in the dotted suffix, such as `AD_AG0`, `DN_EVEN`, `CH0`, or `TxC_CYCLES_FULL_AK`. If a suffix does not match the description or mask, users may select the wrong metric. One visible oddity in this chunk is `UNC_M2M_TxR_VERT_STARVED1.TGC`: its brief and public descriptions still say "AKC - Agent 0" while the event name suffix is `TGC` and the mask is `0x4`. That may be intentional hardware nomenclature reuse or a documentation copy/paste issue, but it is worth preserving as-is unless checked against the vendor event source.

Description quality varies. Several UBOX M2U and RACU entries use the event name itself as the brief description and have no public description. That is acceptable for parser behavior but gives weaker `perf list` help text. Ring descriptions also mention "JKT" in TGC public descriptions even though this file is for Snow Ridge X; this may be inherited vendor wording.

The chunk begins mid-object at line 6248. A chunk processor that treats the selected lines as standalone JSON will fail to parse it. Research and reconciliation should reason over complete source objects from the full file, while the final merged document can still reference the requested line interval.

## Test Signals

Useful validation signals for this data are schema, generation, and runtime resolution checks:

- Parse the full `uncore-interconnect.json` file as JSON and confirm the top-level value is an array of event objects.
- Run or rely on perf's PMU-events generation checks to catch missing required fields, malformed hex strings, duplicate incompatible aliases, and invalid counter/unit metadata.
- Use `perf list` on a Snow Ridge X-capable build to verify aliases such as `UNC_M2M_VERT_RING_AD_IN_USE.UP_EVEN`, `UNC_M2M_WR_TRACKER_OCCUPANCY.CH0`, `UNC_U_EVENT_MSG.MSI_RCVD`, and `UNC_U_CLOCKTICKS` are discoverable with the expected unit.
- On matching hardware, run short `perf stat` probes for representative M2M and UBOX aliases and confirm the events open successfully. Hardware availability is required for meaningful runtime counts.
- Compare generated event tables before and after edits; changes in event name, event code, unit mask, unit, counter, package scope, or experimental flags are behavioral changes even though this is a data-only file.
