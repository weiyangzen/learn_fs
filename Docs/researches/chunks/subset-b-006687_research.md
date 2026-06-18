# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/uncore-io.json lines 10853-11088

## Scope

This chunk covers the tail of the Ice Lake Xeon `uncore-io.json` PMU event table in the vendored Linux `tools/perf` tree. The file is static JSON metadata, not executable code. The perf PMU event generator consumes these objects and emits generated C event tables so users can request uncore IO events by symbolic names.

The requested range starts inside the `UNC_M2P_VERT_RING_AD_IN_USE.DN_EVEN` object: lines 10847-10852 contain its opening fields, while line 10853 begins at its `PublicDescription`. The rest of the chunk contains complete event objects and closes the JSON array at line 11088. Including the partially opened first object, this slice covers 22 M2PCIe vertical-ring usage events: four AD events, four AKC events, four AK events, four BL events, two IV events, and four TGC events.

## Purpose

These records expose Ice Lake Xeon M2PCIe uncore IO events for measuring cycles in which vertical ring links are in use at an M2PCIe ring stop. They are intended for low-level IO fabric analysis, especially determining whether traffic is occupying specific vertical ring directions, ring parities, and message classes.

The event families in this chunk are:

- `UNC_M2P_VERT_RING_AD_IN_USE.*` for AD ring usage.
- `UNC_M2P_VERT_RING_AKC_IN_USE.*` for AKC ring usage.
- `UNC_M2P_VERT_RING_AK_IN_USE.*` for AK ring usage.
- `UNC_M2P_VERT_RING_BL_IN_USE.*` for BL ring usage.
- `UNC_M2P_VERT_RING_IV_IN_USE.*` for IV ring usage.
- `UNC_M2P_VERT_RING_TGC_IN_USE.*` for TGC ring usage.

Each event counts cycles where the named vertical ring is being used at the ring stop, including packets passing by or being sunk. The descriptions explicitly exclude packets being sent from the ring stop, so these are not total injection counters.

## Important Data Fields

Each JSON object follows the perf PMU event schema used under `tools/perf/pmu-events`:

- `EventName` is the symbolic name exposed to `perf list` and accepted by `perf stat -e`.
- `EventCode` selects the M2PCIe hardware event family. This chunk uses `0xb0` for AD, `0xb1` for AK, `0xb2` for BL, `0xb3` for IV, `0xb4` for AKC, and `0xb5` for TGC.
- `UMask` selects direction and parity. `0x1` maps to up/even, `0x2` to up/odd, `0x4` to down/even or down for IV, and `0x8` to down/odd.
- `Counter` is `"0,1,2,3"` for all records, indicating these events can be scheduled on any of the four listed M2PCIe uncore counters.
- `Unit` is `"M2PCIe"` throughout the chunk, binding the events to M2PCIe uncore PMUs rather than core PMUs or other uncore units.
- `PerPkg` is `"1"` throughout, marking the events as package-scoped.
- `Experimental` is `"1"` throughout, warning consumers that these event definitions may be less stable or less broadly validated than non-experimental events.
- `BriefDescription` and `PublicDescription` provide user-facing summaries and longer `perf list --details` text.

## APIs, Types, And Generated Representation

There are no local functions, classes, or C types defined in this JSON file. Its API surface is the generated PMU event metadata:

- `tools/perf/pmu-events/jevents.py` traverses CPU model JSON files and generates `pmu-events.c`.
- `struct pmu_event` in `tools/perf/pmu-events/pmu-events.h` carries generated fields such as `name`, `event`, `desc`, `long_desc`, `pmu`, `unit`, and `perpkg`.
- `pmu_events_table__for_each_event()` iterates generated event records for display and alias construction.
- `pmu_events_table__find_event()` resolves a symbolic event name against the generated model table.
- Runtime perf commands such as `perf list` and `perf stat -e` consume these generated aliases and program the matching uncore PMU event selectors through the kernel perf event interface.

For this chunk, `EventCode`, `UMask`, `Counter`, `Unit`, and `PerPkg` are the operational fields. The descriptions are metadata for users, but mistakes in `EventCode` or `UMask` would change the hardware counter programmed by perf.

## Control Flow

The JSON has no direct runtime control flow. Its effective build and runtime flow is:

1. The perf build runs the PMU event generation path.
2. `jevents.py` reads `tools/perf/pmu-events/arch/x86/icelakex/uncore-io.json` along with the other Ice Lake Xeon topic JSON files.
3. The generator validates each event object and emits generated event-table entries.
4. The generated tables are compiled into perf.
5. At runtime, perf maps matching Intel CPUID patterns from `arch/x86/mapfile.csv` to the `icelakex` directory.
6. `perf list` exposes names such as `UNC_M2P_VERT_RING_TGC_IN_USE.UP_ODD`.
7. `perf stat -a -e <event>` or similar commands resolve the symbolic name and ask the kernel uncore PMU driver to program the package-level M2PCIe counter.

The chunk is ordered by ring/message class: AD, AKC, AK, BL, IV, then TGC. Within most families the records follow down/even, down/odd, up/even, up/odd. The IV family has only `DN` and `UP`, because the description says there is only one IV ring.

## State And Persistence Behavior

The persistent state is the checked-in JSON metadata plus the generated perf event table produced at build time. This source does not create files, mutate process state, persist measurements, or hold runtime state.

At runtime, the measured state lives in M2PCIe uncore hardware counters. These counters accumulate ring-use cycles for package-level IO fabric PMUs. Because `PerPkg` is set, results should be interpreted as package-scoped uncore measurements, not per-thread or per-core counts.

The distinction between passing/sunk packets and packets sent from the ring stop is important state semantics. These events describe observed ring occupancy at the stop, not outbound injection by that stop. For AD, AK, AKC, BL, and TGC, direction and parity split the measurement across two physical ring directions and even/odd ring classes. For IV, users must combine direction filters according to the description if they want an even-ring or odd-ring view; the naming does not expose separate even/odd IV event names in this chunk.

## Dependencies And Integration Points

This chunk integrates with the Linux perf PMU event stack:

- `tools/perf/pmu-events/README` documents JSON topic files, `mapfile.csv`, and generation of `pmu-events.c`.
- `tools/perf/pmu-events/jevents.py` parses these records and emits generated C tables.
- `tools/perf/pmu-events/pmu-events.h` defines the generated event-table interface.
- `tools/perf/pmu-events/arch/x86/mapfile.csv` maps Ice Lake Xeon CPUID patterns `GenuineIntel-6-6[AC]` to the `icelakex` PMU event directory.
- The Linux x86 uncore PMU driver must expose compatible M2PCIe PMUs and counters for these aliases to work on real hardware.

Although the source path is under `sources/distributed-fs/ceph-client`, this file belongs to a vendored Linux perf tooling subtree. It has no direct CephFS client, distributed filesystem protocol, metadata-server, network IO, or storage control-flow integration.

## Event Family Notes

The AD, AK, AKC, BL, and TGC families each model a four-way direction/parity split:

- `.UP_EVEN` uses `UMask: "0x1"`.
- `.UP_ODD` uses `UMask: "0x2"`.
- `.DN_EVEN` uses `UMask: "0x4"`.
- `.DN_ODD` uses `UMask: "0x8"`.

The public descriptions explain that there are clockwise and counter-clockwise rings. On the left side of the ring, UP is clockwise and DN is counter-clockwise; on the right side this is reversed. They also warn that the first half of CBo stops and the second half are on opposite sides, so the same direction label can refer to different physical rings depending on CBo position.

The IV family is different. `UNC_M2P_VERT_RING_IV_IN_USE.DN` uses `UMask: "0x4"` and `.UP` uses `UMask: "0x1"`. The description says there is only one IV ring, then refers to selecting both `UP_EVEN` and `DN_EVEN` or both `UP_ODD` and `DN_ODD`; that text does not line up cleanly with the two exposed event names in this chunk. Consumers should treat IV event interpretation cautiously and verify against Intel uncore documentation or empirical perf behavior.

## Risks And Edge Cases

The first event in the requested range is incomplete when the chunk is viewed alone. Its `BriefDescription`, `Counter`, `EventCode`, `EventName`, `Experimental`, and `PerPkg` fields are on lines 10847-10852, just before the requested start. The merge lane must use adjacent chunks or full-file context before validating object completeness.

All events are marked experimental. Tooling should still parse and expose them, but users should be aware that names, masks, or descriptions may have weaker stability guarantees.

Several public descriptions contain rough inherited wording, including references to `JKT`, the phrase `We really have two rings in --`, and spacing issues such as missing spaces after periods. These are user-facing strings in perf output. Cleaning them up can improve readability, but doing so should not be mixed with semantic changes to event codes or masks.

The direction/parity mapping is easy to misread. A single swapped `UMask` between `UP_ODD` and `DN_EVEN`, for example, would still be valid JSON and likely still build, but it would silently measure the wrong physical ring class.

The final TGC object is followed by the file-closing `]` and has no trailing comma. Any edit at this tail must preserve complete JSON array syntax for the entire `uncore-io.json` file.

## Test Signals

Useful validation signals for this chunk include:

- Running JSON validation on the complete `icelakex/uncore-io.json`, not on this partial line slice alone.
- Running the perf PMU event generation path and confirming `pmu-events.c` generation succeeds without schema or parse errors.
- Building perf with generated PMU events enabled.
- Running perf PMU event tests that exercise generated table lookup, especially code paths using `pmu_events_table__find_event()`.
- Using `perf list --details` on an Ice Lake Xeon-capable perf build to spot-check events such as `UNC_M2P_VERT_RING_AD_IN_USE.DN_EVEN`, `UNC_M2P_VERT_RING_AK_IN_USE.UP_ODD`, `UNC_M2P_VERT_RING_IV_IN_USE.UP`, and `UNC_M2P_VERT_RING_TGC_IN_USE.DN_ODD`.
- On Ice Lake Xeon hardware with M2PCIe uncore PMUs exposed, running package-wide `perf stat` for representative UP/DN and even/odd variants and confirming scheduling succeeds and counts are plausible under IO traffic.

## Cross-Chunk Notes

This document intentionally covers only lines 10853-11088. Earlier chunks contain the opening fields for the first AD event in this range and the preceding M2PCIe event families. The final per-file research document should reconcile this tail chunk with prior chunks before making whole-file claims about total event counts or family coverage.
