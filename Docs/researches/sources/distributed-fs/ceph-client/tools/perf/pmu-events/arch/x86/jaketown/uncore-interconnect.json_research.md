# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-interconnect.json

## Purpose

`uncore-interconnect.json` defines 207 Jaketown uncore interconnect PMU events consumed by perf's JSON event-table generation path. The file covers socket/package interconnect and system-agent style units rather than core pipeline events. Its records describe event aliases, event select codes, unit masks, allowed counter sets, package scope, and user-facing descriptions for the IRP, QPI, R3QPI, and UBOX units.

This file is data, but it behaves like an API contract for perf users and for the generated event tables. Names such as `UNC_Q_RxL_FLITS_G1.HOM_REQ` or `UNC_R3_RING_AD_USED.CW_EVEN` become stable event identifiers that can be requested through `perf stat`/`perf list` on matching Sandy Bridge-EP/Jaketown systems.

## Important API Surface and Data Shape

Each entry is a JSON object with common keys:

- `EventName`: public perf event alias. All 207 names are unique.
- `EventCode`: hardware event select value where required. Some clock or special QPI transfer entries omit this field.
- `UMask`: unit-mask selector where required. Some clock/simple events omit it.
- `Unit`: uncore PMU unit selector. This file uses `IRP`, `QPI`, `R3QPI`, and `UBOX`.
- `Counter`: comma-separated list of compatible hardware counter indexes.
- `PerPkg`: package-level scoping flag, consistently present for these uncore records.
- `BriefDescription` and usually `PublicDescription`: short and expanded event help text.

The main event families are:

- `IRP` (36 events): address-match stalls/merges, outstanding read/write/cache occupancy, IRP clockticks, receive ring insert/occupancy/full cycles, tickle events, transaction reads/writes/prefetches, transmit request/data insertions, and write-ordering stall cycles. IRP records use counters `0,1`.
- `QPI` (84 events): QPI clockticks, Direct2Core success/failure, link power cycles, receive/transmit link bypass, CRC/no-credit conditions, VN0/VNA credits, cycles-not-empty, flit classification for G0/G1/G2, link insert/occupancy, and stall reasons. QPI records generally allow counters `0,1,2,3`.
- `R3QPI` (63 events): ring and QPI interface bridge events including IIO credits acquired/used/rejected, AD/AK/BL ring used by direction and parity, IV usage, receive ring bypass/cycles/inserts/occupancy, VN0/VNA credit usage/rejects, and VNA credit cycles. Counter constraints vary more here, including single-counter records and combinations such as `0,1,2`.
- `UBOX` (24 events): UBOX clockticks, event-message classes, filter-match variants, lock cycles, message channel size, PHOLD cycles, RACU request count, and U2C monitor/error/trap message classes.

## Control Flow

There is no runtime control flow inside the file. The effective flow is external:

1. perf's PMU event-table generator reads architecture/model JSON files from `tools/perf/pmu-events/arch/x86/jaketown`.
2. Each JSON object is validated and converted into generated C table entries.
3. At runtime, perf matches the CPU model to the Jaketown table and exposes these aliases through `perf list`.
4. A user-selected alias is resolved into the encoded uncore PMU config using `EventCode`, `UMask`, `Unit`, and any filter fields.
5. The kernel/perf uncore driver programs the selected uncore PMU counter if the `Unit` and `Counter` constraints match available hardware.

Ordering in the file is meaningful for maintainability and generated help output: related umask variants are grouped together under a shared event prefix.

## State and Persistence Behavior

The file has no mutable state. Its persistent state is the checked-in JSON array. The hardware counters it describes are volatile PMU registers, but this file only maps symbolic names to encodings. Changes to event names, unit masks, or counter lists persist into generated perf event tables and can alter user-facing CLI compatibility.

All records are package-scoped through `PerPkg: "1"`, which matters for multi-socket aggregation: users should expect counts to represent uncore/package domains, not per-thread or per-core execution.

## Dependencies and Integration Points

Dependencies are structural rather than imported:

- The JSON schema expected by perf's `pmu-events` generator.
- Jaketown uncore PMU naming and encoding conventions.
- Matching uncore PMU unit names (`IRP`, `QPI`, `R3QPI`, `UBOX`) understood by perf's generated tables and runtime PMU discovery.
- Adjacent Jaketown files such as `uncore-io.json`, `uncore-memory.json`, and `uncore-power.json`, which complete the platform event catalog.

Integration risks are highest at the boundary where JSON strings become generated C constants. `Counter` is encoded as a string list, not a structured array, so formatting must remain compatible with the parser. Missing `EventCode` or `UMask` values are expected for some records, but consumers must distinguish intentional omissions from malformed event definitions.

## Risks and Edge Cases

- The file has 12 records without `EventCode` and 55 without `UMask`; this is valid for some event classes but should be covered by generator validation so absent fields are not silently mis-encoded.
- `UNC_U_CLOCKTICKS` lacks both `EventCode` and public/brief description content beyond its name, making generated help weaker than neighboring records.
- Some QPI flit transfer records omit `EventCode` while related receive-side records include codes; regressions in parser defaults could break only these aliases.
- `R3QPI` counter lists are less uniform than the QPI records. A mistaken broadening to `0,1,2,3` could allow invalid scheduling on hardware.
- Description text uses hardware abbreviations (`DRS`, `HOM`, `NCB`, `NCS`, `NDR`, `SNP`, `VNA`) without local glossary. That is acceptable for perf PMU tables but increases user interpretation risk.
- Because event names are public aliases, renaming or re-casing any name is a compatibility break for scripts that call `perf stat -e`.

## Test Signals

Useful validation signals include:

- `jq` parse succeeds and the root is an array of 207 objects.
- `EventName` uniqueness holds across all 207 entries.
- Required schema fields are present where expected: `EventName`, `Unit`, `Counter`, `BriefDescription`, and `PerPkg` for every entry.
- All `Unit` values are in the expected set: `IRP`, `QPI`, `R3QPI`, `UBOX`.
- Generated perf event tables build without pmu-events warnings.
- `perf list` on a supported Jaketown system shows representative aliases from each unit family.
- Hardware smoke tests can attempt `perf stat -e` for `UNC_I_CLOCKTICKS`, one QPI flit event, one R3QPI ring event, and one UBOX message event, verifying that counter constraints are accepted.
