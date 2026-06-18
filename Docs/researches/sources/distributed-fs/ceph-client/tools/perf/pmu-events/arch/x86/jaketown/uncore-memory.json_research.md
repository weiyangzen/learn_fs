# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/uncore-memory.json

## Purpose

`uncore-memory.json` defines 51 Jaketown integrated memory controller (`iMC`) uncore PMU events. These records let perf users observe DRAM command traffic, memory-controller modes, power states, throttling, refresh behavior, ECC correctable errors, read/write pending queue pressure, precharge behavior, and queue hit activity.

The file is the memory-controller event catalog for the Jaketown platform. It is declarative, but it forms the stable event alias and encoding API used by perf.

## Important API Surface and Data Shape

The file is a JSON array of 51 unique objects. Common keys are `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, `Unit`, and often `UMask` and `PublicDescription`.

All records use `Unit: "iMC"` and `PerPkg: "1"`. All visible counter lists allow `0,1,2,3`.

Important event families:

- Command counters: `UNC_M_ACT_COUNT`, `UNC_M_CAS_COUNT.*`, `UNC_M_DRAM_PRE_ALL`, and `UNC_M_PRE_COUNT.*`.
- CAS breakdowns: `UNC_M_CAS_COUNT.RD`, `RD_REG`, `RD_UNDERFILL`, `WR`, `WR_RMM`, `WR_WMM`, and `ALL`, all sharing event code `0x4` with different masks.
- DRAM maintenance and reliability: `UNC_M_DRAM_REFRESH.HIGH`, `UNC_M_DRAM_REFRESH.PANIC`, and `UNC_M_ECC_CORRECTABLE_ERRORS`.
- Controller mode occupancy: `UNC_M_MAJOR_MODES.ISOCH`, `PARTIAL`, `READ`, and `WRITE`.
- Power behavior: channel DLL off, precharge power-down, CKE cycles per rank, critical throttle cycles, self refresh, and throttle cycles per rank.
- Queue pressure: read pending queue cycles full/not-empty, inserts, occupancy; write pending queue cycles full/not-empty, inserts, occupancy; WPQ read/write hit.
- Preemption events: read-preempt-read and read-preempt-write.

## Control Flow

There is no executable control flow. Externally:

1. perf's pmu-events generator reads the JSON array.
2. It converts each `UNC_M_*` object into generated event table rows.
3. Runtime CPU matching selects the Jaketown table.
4. perf exposes the aliases in `perf list`.
5. User-selected aliases are translated into iMC PMU event codes and masks, then programmed on available memory-controller counters.

The file groups related masks together, especially CAS and rank-specific power/throttle events, making manual review easier and reducing accidental cross-family drift.

## State and Persistence Behavior

The file persists static hardware metadata. It does not mutate state or hold runtime measurements. The actual PMU counts are hardware state outside the repository.

Package scoping through `PerPkg: "1"` means measurements are package/socket-level uncore observations. On platforms with multiple memory controllers or channels, users and tooling must account for aggregation semantics supplied by perf and the kernel uncore driver.

## Dependencies and Integration Points

This source depends on:

- perf's PMU event JSON schema.
- Jaketown iMC event encodings, masks, and rank semantics.
- Generated C event tables in the perf build.
- The kernel/perf uncore iMC PMU support for this CPU family.

It integrates with other Jaketown uncore files for whole-system bottleneck analysis. For example, `uncore-memory.json` queue occupancy and CAS counts can be interpreted alongside QPI/R2/R3 interconnect events from the adjacent JSON files.

## Risks and Edge Cases

- Seven CAS records lack `PublicDescription` and rely only on `BriefDescription`; generated help remains useful but less detailed.
- Eighteen records omit `UMask`; this is expected for simple selector events but should be schema-validated.
- `UNC_M_CLOCKTICKS` lacks `EventCode`, so parser defaults and clock-event handling must remain compatible.
- Rank-specific events (`RANK0` through `RANK7`) are repetitive. A copied event code or rank mapping error would be difficult to detect from syntax alone.
- Several power/throttle families use nearby event codes and identical counter lists; semantic regressions may only appear under hardware validation.
- `UNC_M_CAS_COUNT.ALL` has a brief description that mentions write CAS despite the name implying combined read/write CAS. This may be inherited vendor text, but it is a documentation ambiguity worth preserving or correcting only against authoritative hardware docs.

## Test Signals

- `jq` parse succeeds and reports 51 unique event names.
- Every record has `Unit == "iMC"` and `PerPkg == "1"`.
- CAS family masks should be checked for expected bit combinations: read regular/underfill and write read-major/write-major modes compose into broader read/write/all aliases.
- Rank families should contain exactly RANK0 through RANK7 for both CKE and throttle cycles.
- Generated pmu-events code should build without warnings.
- On supported hardware, representative smoke tests should include `UNC_M_ACT_COUNT`, `UNC_M_CAS_COUNT.RD`, `UNC_M_RPQ_OCCUPANCY`, and one rank-specific power event.
