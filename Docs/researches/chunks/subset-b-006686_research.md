# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-io.json lines 5326-10852

## Scope

This chunk covers a large middle-to-late slice of the Ice Lake Xeon `uncore-io.json` PMU event table used by the vendored Linux `tools/perf` PMU event machinery. The range is declarative event metadata, not executable Ceph client logic.

The requested line range begins after the opening fields of `UNC_M2P_AG0_AD_CRD_OCCUPANCY0.TGR2`; the first complete event in the chunk is `UNC_M2P_AG0_AD_CRD_OCCUPANCY0.TGR3`. It ends inside the next event object, after the `EventName` for `UNC_M2P_VERT_RING_AD_IN_USE.DN_EVEN`; that object continues in the following chunk. Counting by `EventName` lines in the requested range, this slice contains 515 event-name occurrences, 514 complete `Unit` fields, and all visible events belong to the `M2PCIe` uncore PMU unit.

## Purpose

The file defines user-visible perf event names and their hardware encodings for Ice Lake Xeon uncore I/O monitoring. Perf consumes entries from this JSON to map event strings such as `UNC_M2P_IIO_CREDITS_USED.NCB_0` or `UNC_M2P_TxR_HORZ_OCCUPANCY.AD_CRD` to event select values, unit masks, counter constraints, package scope, and descriptions.

This chunk is specifically the M2PCIe/Common Mesh Stop portion of the table. It describes events for M2PCIe-to-IIO credits, CMS ingress and egress queues, horizontal and vertical mesh rings, agent/transgress credit use, starvation, NACKs, queue occupancy, queue-full/non-empty cycles, anti-deadlock-slot usage, and ring bounce/sink behavior. These events let perf users diagnose package-level I/O and mesh pressure rather than Ceph data-path behavior.

## Important Data and Event Families

Every visible event uses the perf PMU JSON schema: `BriefDescription`, `Counter`, `EventCode`, `EventName`, `Experimental`, `PerPkg`, `PublicDescription` where available, `UMask`, and `Unit`. Almost all entries advertise counters `0,1,2,3`; a smaller group uses `0,1` for narrower counter support. Most entries have `"Experimental": "1"` and all complete entries in this range have `"PerPkg": "1"`, meaning perf treats the event as package-scoped uncore metadata.

The leading family continues `UNC_M2P_AG*_AD/BL_CRD_*` definitions. These break CMS agent 0 and agent 1 AD/BL credit acquisition and occupancy into transgress selectors. Transgresses 0-7 are typically encoded in the `*0` event-code half with power-of-two unit masks, while transgresses 8-10 are represented by the `*1` event-code half. The chunk starts mid-family with agent 0 AD occupancy for transgress 3 and then covers BL credit acquisition/occupancy for agent 0, AD and BL credit acquisition/occupancy for agent 1, and related event-code pairs from `0x82` through `0x8f`.

The IIO credit families include `UNC_M2P_IIO_CREDITS_ACQUIRED`, `UNC_M2P_IIO_CREDITS_REJECT`, and `UNC_M2P_IIO_CREDITS_USED`. Their descriptions identify DRS, NCB, and NCS message classes and CMS port 0/1 splits. These events count acquired credits, failed acquisition attempts, and cycles with credits in use for BL-ring traffic moving from the M2PCIe agent into the IIO.

Peer-to-peer credit families include local and remote dedicated/shared P2P credit taken, returned, and wait events, along with received and occupancy events. Names distinguish local versus remote, dedicated versus shared, taken versus returned, and wait versus occupancy. This lets perf isolate pressure in P2P credit pools rather than only seeing aggregate ring traffic.

Ingress-side CMS families include `UNC_M2P_RxC_*` and `UNC_M2P_RxR_*`. They cover cycles non-empty, inserts, busy-starved, bypass, credit-starved, occupancy, and allocation behavior for traffic received from the mesh into CMS ingress structures. The unit masks further split ring classes such as AD, AK, AKC, BL, and IV, with credited/uncredited/all variants for some families.

Ring health families include horizontal and vertical ring in-use, bounce, source throttle, and sink-starvation events. `UNC_M2P_HORZ_RING_*_IN_USE` covers AD/AK/AKC/BL/IV ring use by direction and even/odd ring where applicable. `UNC_M2P_RING_BOUNCES_HORZ` and `UNC_M2P_RING_BOUNCES_VERT` count bounced incoming messages by ring type. `UNC_M2P_RING_SINK_STARVED_*` captures sink starvation by ring/message class, and `UNC_M2P_RING_SRC_THRTL` provides source-throttle coverage.

Transgress and egress families are heavily represented. `UNC_M2P_TxC_*` covers egress-to-CMS credits, queue full/non-empty cycles, and inserts. `UNC_M2P_TxR_HORZ_*` and `UNC_M2P_TxR_VERT_*` cover horizontal and vertical egress paths: ADS/bypass usage, cycles full, cycles non-empty, inserts, NACKs, occupancy, and injection starvation. These are split by ring type and by CMS agent where the hardware exposes agent-specific masks.

Stall families `UNC_M2P_STALL0_NO_TxR_HORZ_CRD_*` and `UNC_M2P_STALL1_NO_TxR_HORZ_CRD_*` count cycles where AD or BL agent egress buffers are stalled waiting for transgress credits. As with the credit families, the event-code suffix splits transgress 0-7 from transgress 8-10.

The chunk ends by starting the vertical ring in-use family with `UNC_M2P_VERT_RING_AD_IN_USE.DN_EVEN`. The complete object and the rest of the vertical ring in-use definitions continue after the requested line range.

## Control Flow

There is no in-file control flow. Runtime behavior is provided by perf's generated PMU event tables:

1. Perf detects the Ice Lake Xeon CPU model and selects the `arch/x86/icelakex` event metadata.
2. A user or tool requests an event by `EventName`.
3. Perf resolves the matching JSON object and checks the counter constraint, package scope, and PMU unit.
4. Perf programs the `M2PCIe` uncore PMU with the entry's `EventCode` and `UMask`.
5. Hardware accumulates counts for the selected queue, credit, ring, NACK, stall, starvation, or occupancy condition until perf reads the counter.

The apparent structure in this chunk is generated by hardware event decomposition rather than code branching. Event-code pairs, such as `*0` and `*1` families, extend one conceptual metric across more unit-mask selectors than one event code can carry. Perf does not infer those relationships from names; it consumes the explicit object for each event.

## State and Persistence Behavior

The JSON is static metadata. It does not store measurements and has no mutable state inside Ceph or perf. Its persistence behavior is repository/build persistence: changing an event name, code, mask, counter list, or description changes how built perf exposes Ice Lake Xeon uncore events.

At runtime, state exists in hardware PMU counters and perf event attributes. `PerPkg` indicates package-level accounting, so counts are tied to the package/uncore instance rather than a process, core, or thread. Many events are occupancy or cycles-in-condition metrics; their values depend on elapsed measurement time and need normalization against clockticks or a related cycle event for rate analysis.

The `Experimental` flag is persistent metadata too. It signals that these M2PCIe events may be less stable or less generally validated than non-experimental events, while still making them available to perf users.

## Dependencies and Integration Points

This file integrates with the Linux perf PMU event parser, generated perf event tables, and the Ice Lake Xeon uncore M2PCIe PMU. It is present under `sources/distributed-fs/ceph-client` as vendored Linux tooling data, so the relevant integration surface is perf, not Ceph's filesystem client runtime.

The event definitions depend on Intel's uncore hardware encodings for the `M2PCIe` unit. Correctness requires `EventCode`, `UMask`, `Counter`, and package-scope metadata to match the CPU model's PMU programming interface. The ring names and message-class names depend on Intel mesh terminology: AD, AK, AKC, BL, IV, DRS, NCB, NCS, credited/uncredited traffic, CMS agents, CMS ports, and transgress buffers.

Perf-side integration is name-driven. Scripts, dashboards, tests, and documentation can request these exact `UNC_M2P_*` names. Any rename or mask change has compatibility impact even though the file is data-only.

## Risks and Edge Cases

Chunk-boundary parsing is the first risk. The requested range starts and ends inside event objects, so the chunk alone is not valid JSON and should not be used as an independent parser fixture. Full-file validation must parse `uncore-io.json` as a whole.

The event families are highly repetitive, making copy/paste drift plausible. Common risks are swapped agent numbers, local versus remote P2P confusion, dedicated versus shared credit confusion, credited/uncredited/all mask drift, horizontal versus vertical ring mix-ups, and transgress 8-10 entries assigned to the wrong `*1` event code or unit mask.

Some descriptions appear inconsistent with names. For example, several `CYCLES_FULL` descriptions say "Not Full", and the final visible `UNC_M2P_TxR_VERT_STARVED1.TGC` entry describes "AKC - Agent 0" even though the event name is `TGC`. These may reflect upstream metadata quirks, but they are important because users often rely on `PublicDescription` for interpretation.

Case and formatting should be preserved. The chunk contains both `0x2D` and `0x2d` event-code spellings for `UNC_M2P_TxC_CREDITS.*`; JSON parsers accept both as strings, but tooling or tests that canonicalize encodings should avoid treating harmless case differences as semantic changes.

Many entries are package-level uncore events with counter constraints. Running several events from the same counter-constrained set at once may require multiplexing or may fail depending on perf/kernel scheduling. Interpreting occupancy and starvation counters without a cycle baseline can lead to misleading conclusions.

Hardware availability is model-specific. These names belong to `icelakex`; using them on another CPU family, or with a kernel/perf build whose uncore PMU support differs, may fail or count different hardware behavior.

## Test Signals

Useful validation starts with strict parsing of the complete `uncore-io.json` file and a schema check for every event object. For this chunk, checks should confirm that complete objects have `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, and `PerPkg`, with `Unit` equal to `M2PCIe` for the complete entries in range.

Generated perf event-table tests should verify representative names from each family: `UNC_M2P_AG1_BL_CRD_OCCUPANCY1.TGR10`, `UNC_M2P_IIO_CREDITS_REJECT.NCS`, `UNC_M2P_LOCAL_SHAR_P2P_CRD_WAIT_0.*`, `UNC_M2P_RxR_OCCUPANCY.*`, `UNC_M2P_RING_BOUNCES_VERT.BL`, `UNC_M2P_STALL0_NO_TxR_HORZ_CRD_AD_AG0.TGR0`, `UNC_M2P_TxC_CYCLES_FULL.*`, `UNC_M2P_TxR_HORZ_NACK.*`, and `UNC_M2P_TxR_VERT_STARVED1.*`.

Encoding tests should sample families with split event-code halves and confirm the transgress-to-mask mapping: transgresses 0-7 use masks `0x1` through `0x80` on the base event code, while transgresses 8-10 use masks `0x1`, `0x2`, and `0x4` on the paired event code.

Runtime smoke tests on Ice Lake Xeon hardware should use `perf list` to confirm the names are exposed under the M2PCIe/uncore unit, then run `perf stat` on low-risk representative events. Traffic-producing tests should exercise PCIe/IIO paths to see non-zero IIO credit counts, mesh pressure tests should affect RxR/TxR occupancy or inserts, and idle baselines should remain low for NACK/starvation events.

Documentation tests should flag mismatches between `EventName`, `BriefDescription`, and `PublicDescription`, especially the `CYCLES_FULL` text and `TGC`/`AKC` wording. These are not parser failures, but they are user-facing interpretation risks.

## Cross-Chunk Notes

The previous chunk is required to reconstruct the full `UNC_M2P_AG0_AD_CRD_OCCUPANCY0.TGR2` object and the earliest portion of the agent 0 AD occupancy family. The next chunk is required to finish `UNC_M2P_VERT_RING_AD_IN_USE.DN_EVEN` and cover the rest of the vertical ring in-use definitions.

The merge lane should combine this with other chunks for `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-io.json` before producing a final per-file report, because this document intentionally describes only the requested line slice and its immediate boundary context.
