# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/memory.json

## Purpose

`memory.json` defines Knights Landing perf aliases for memory-ordering machine clears and offcore-response memory-source breakdowns. It contains 101 records: one `MACHINE_CLEARS.MEMORY_ORDERING` event and 100 `OFFCORE_RESPONSE` events focused on DDR, MCDRAM, near/far locality, and non-DRAM responses.

The file lets users ask memory-source questions such as whether demand data reads, RFOs, prefetches, partial reads/writes, or code reads are served by local/far DDR, local/far MCDRAM, or non-DRAM address space.

## Important APIs, Types, and Schema

The file follows the perf event JSON schema with fields `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and, for offcore rows, `MSRIndex` and `MSRValue`.

Important event families are:

- `MACHINE_CLEARS.MEMORY_ORDERING`, `EventCode: "0xC3"`, `UMask: "0x2"`, for machine clears caused by memory-ordering hazards.
- `OFFCORE_RESPONSE.<request>.<source>`, almost all using `EventCode: "0xB7"` and `UMask: "0x1"`.

Offcore request classes include any code/data/read/request/RFO, bus locks, demand code/data/RFO, partial reads/writes, L1 data prefetches, L2 code/RFO prefetches, software prefetches, and UC code reads. Response/source classes include `DDR`, `DDR_NEAR`, `DDR_FAR`, `MCDRAM`, `MCDRAM_NEAR`, `MCDRAM_FAR`, and `NON_DRAM`.

Most offcore rows allow `MSRIndex: "0x1a6,0x1a7"`. Partial writes use `MSRIndex: "0x1a7"` because the descriptions say they should be programmed on PMC1. All rows list `Counter: "0,1"`, so the MSR field is the more specific hardware-programming constraint.

## Control Flow and Data Flow

Perf parses the event table, maps a requested alias to core event `0xB7/0x1`, and writes the listed offcore response filter into the selected offcore MSR. The MSR value combines request bits with response/source bits, so the named event controls both what traffic type is counted and where the response came from.

In use, these events are generally compared across source variants. For example, the DDR and MCDRAM variants of `DEMAND_DATA_RD` expose placement/locality differences, while `DDR_NEAR` versus `DDR_FAR` can reveal NUMA/tile-distance effects.

## State and Persistence Behavior

The JSON is static source metadata. Runtime state exists only when perf opens events and programs PMU registers/MSRs. Because offcore MSR filters are shared hardware resources, concurrent offcore events may be constrained by available counters and MSR slots even when each event descriptor looks independently valid.

## Dependencies and Integration Points

The file depends on perf's KNL event-map parser and the core offcore-response event implementation. It integrates closely with `cache.json`: both files use `OFFCORE_RESPONSE`, but `cache.json` focuses on L2/tile cache-response classes while `memory.json` focuses on DDR, MCDRAM, and non-DRAM source classes.

It also integrates with `counter.json` for core counter capacity and with system topology/runtime memory configuration. The semantic value of DDR versus MCDRAM near/far events depends on KNL memory mode and placement.

## Risks and Edge Cases

The largest risk is misprogramming or misinterpreting offcore MSR selectors. The file contains many similar rows whose only differences are `EventName`, `MSRValue`, and brief source text. A single wrong bit in `MSRValue` changes the measured memory source.

Partial-read descriptions note UC/WC outstanding semantics, while partial-write descriptions specify PMC1/`0x1a7`. Consumers that only honor `Counter: "0,1"` may schedule events in invalid combinations. `NON_DRAM` rows include MMIO transactions, so they should not be read as ordinary memory bandwidth.

`MACHINE_CLEARS.MEMORY_ORDERING` belongs to the machine-clear family rather than the offcore matrix, so scripts assuming every memory file row has `MSRIndex` will fail.

## Test Signals

Validation should parse the JSON, confirm 101 records, verify one `MACHINE_CLEARS` row and 100 `OFFCORE_RESPONSE` rows, check unique `EventName` values, and ensure every offcore row has `MSRIndex` and `MSRValue`. Cross-checks should verify expected near/far/source families and that partial-write events use `0x1a7`. Runtime or generated-table tests should expose representative DDR, MCDRAM, and non-DRAM aliases through `perf list` and open a small event set without parser errors.
