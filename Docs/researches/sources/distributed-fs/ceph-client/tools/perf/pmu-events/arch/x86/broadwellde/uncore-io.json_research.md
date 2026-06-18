# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/uncore-io.json

## Purpose

`uncore-io.json` is a Broadwell-DE perf PMU event table for the R2PCIe uncore block. It contributes Intel model-specific aliases that let users refer to R2PCIe ring, IIO-credit, queue, and stall counters by symbolic names such as `UNC_R2_RING_AD_USED.ALL` rather than by raw uncore event encodings. The file is data, not executable code, but it is part of perf's build-time event database and therefore participates in the generated `pmu-events.c` tables used by `perf list`, event parsing, Python export, and PMU alias lookup.

The table contains 62 JSON objects, all scoped to `Unit: "R2PCIe"` and `PerPkg: "1"`. Every entry has an `EventCode`; all but `UNC_R2_CLOCKTICKS` also carry a `UMask`. The counters are package-level uncore counters, so they describe socket/package R2PCIe behavior rather than per-task or per-core attribution.

## Important APIs, Types, and Data Shape

Each object uses the perf PMU JSON schema fields consumed by `tools/perf/pmu-events/jevents.py`: `EventName`, `EventCode`, optional `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and often `PublicDescription`. During the perf build, `jevents.py` converts these records into generated C data in `pmu-events/pmu-events.c`, represented at runtime through the `pmu-events.h` event-table structures. `util/pmu.c` then exposes the generated entries as PMU aliases, and `builtin-list.c` prints their descriptions and encodings.

The important semantic API here is the stable event naming convention:

- `UNC_R2_CLOCKTICKS` is the baseline uncore clock-domain counter.
- `UNC_R2_IIO_CREDIT.*`, `UNC_R2_IIO_CREDITS_ACQUIRED.*`, and `UNC_R2_IIO_CREDITS_USED.*` describe IIO credit availability, acquisition, and in-use cycles for QPI and message classes.
- `UNC_R2_RING_{AD,AK,BL,IV}_USED.*` describe ring traffic occupancy by ring, direction, and polarity.
- `UNC_R2_RING_AK_BOUNCES.*` tracks AK ingress bounce events.
- `UNC_R2_RxR_*` and `UNC_R2_TxR_*` cover receive/transmit ring occupancy, non-empty/full cycles, inserts, and clockwise NACKs.
- `UNC_R2_SBO0_*` and `UNC_R2_STALL_NO_SBO_CREDIT.*` cover SBO credit acquisition, occupancy, and stalls.

Counters are declared as string lists such as `0,1` or `0,1,2,3`, which the generated alias metadata passes through to perf's PMU constraint logic. The unit string is the binding point to the kernel's R2PCIe uncore PMU name matching; if the running kernel does not expose a matching PMU, the aliases remain unavailable or unresolvable.

## Control Flow

There is no runtime control flow in the JSON itself. The effective control flow is:

1. The x86 `mapfile.csv` maps Broadwell-DE CPUs (`GenuineIntel-6-56`) to the `broadwellde` event directory.
2. The perf build copies or reads `pmu-events/arch/x86/broadwellde/uncore-io.json` through `pmu-events/Build`.
3. `jevents.py` parses the array, normalizes field names, and emits C table rows with event name, unit, event code, mask, counter constraints, package scope, and descriptions.
4. At runtime, perf chooses the generated table matching the host CPU model, looks up events for discovered PMUs, and exposes the aliases in `perf list` and event parsing.
5. When a user records or stats one of these aliases, perf resolves the alias to the raw R2PCIe uncore event selector and opens the corresponding perf event on the package PMU.

The file's order is also user-visible in generated event listings, so broad family grouping and stable ordering matter for review diffs and list output.

## State and Persistence Behavior

The source file is static repository data. Build products persist a transformed copy in generated `pmu-events.c` and `libpmu-events.a`; runtime state is limited to perf's in-memory PMU alias tables and opened perf-event file descriptors. The events themselves count hardware state in the R2PCIe unit while counters are enabled. `PerPkg: "1"` means results should be interpreted as package-level measurements, not process-local state.

No state is written back to this JSON. Changing an event name, code, mask, unit, or description affects all later perf builds and can break scripts that rely on alias strings.

## Dependencies and Integration Points

The file depends on the x86 PMU-event generator, the Broadwell-DE mapfile row, the kernel exposing compatible Intel uncore R2PCIe PMUs, and perf's PMU alias machinery. It integrates with `perf list` default and JSON output, `perf stat -e <alias>`, `perf record` where uncore sampling is supported, and Python dictionary export of PMU events. It is adjacent to other `broadwellde` core and uncore JSON files, which together form the model's complete event database.

The descriptions rely on Intel Broadwell-DE uncore event semantics. They distinguish cycles-in-use counters from discrete insert/acquire/bounce/NACK counters, which is important because users may combine them into ratios such as occupancy per clocktick or stalls per transfer.

## Risks and Edge Cases

The largest correctness risk is metadata drift from Intel's event specification: a wrong `EventCode`, `UMask`, or `Unit` silently produces wrong measurements or an alias that cannot be programmed. `UNC_R2_CLOCKTICKS` intentionally lacks `UMask`; validation should treat this as a clock event rather than a malformed entry. Ring-use masks combine direction and even/odd polarity, so copy/paste errors among `CW`, `CCW`, `*_EVEN`, and `*_ODD` entries are easy to miss in plain JSON review.

The file uses only R2PCIe package events, so applying these aliases on non-Broadwell-DE hardware or kernels without matching uncore PMUs should fail gracefully. Public descriptions contain nuanced wording about what is included and excluded, such as packets passing by versus sent from the ring stop; losing those descriptions would make derived analysis easier to misinterpret.

## Test Signals

Useful checks include `jq` parsing, schema checks for required fields, duplicate `EventName` detection, verification that every non-clock event has an `UMask`, and comparison against Intel Broadwell-DE uncore tables. Build-level validation should regenerate `pmu-events.c` without generator warnings and run perf's PMU-event tests. Runtime signals include `perf list --unit R2PCIe`, `perf list --json` showing the R2PCIe aliases, and `perf stat -e UNC_R2_CLOCKTICKS,UNC_R2_RING_AD_USED.ALL` on Broadwell-DE hardware.
