# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/memory.json

## Purpose

`memory.json` defines 131 Skylake PMU events for memory latency, L3 miss behavior, transactional memory, memory ordering clears, offcore response classes, and load-latency precise events. It complements `cache.json`: `cache.json` includes broad cache-hit and offcore-hit coverage, while this file emphasizes L3 misses, local DRAM miss classes, transactional abort causes, and load latency thresholds.

The largest cluster is 88 `OFFCORE_RESPONSE.*` entries for L3 miss and local DRAM combinations across demand code reads, demand data reads, demand RFOs, and other requests. Other clusters cover `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, `HLE_RETIRED.*`, `RTM_RETIRED.*`, `TX_EXEC.*`, `TX_MEM.*`, `CYCLE_ACTIVITY.*`, and `MACHINE_CLEARS.MEMORY_ORDERING`.

## Important schema/API surface

Key entries and fields:

- `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_4` through `LOAD_LATENCY_GT_512`: precise load latency threshold events using MSR index `0x3F6`, `PEBS: 2`, and `Data_LA: 1`.
- `OFFCORE_RESPONSE.*.L3_MISS*` and `.L3_MISS_LOCAL_DRAM.*`: offcore response events using MSR index `0x1a6,0x1a7` and detailed `MSRValue` filters.
- `CYCLE_ACTIVITY.CYCLES_L3_MISS` and `STALLS_L3_MISS`: cycle/stall signals for L3 miss impact.
- `HLE_RETIRED.*`, `RTM_RETIRED.*`, `TX_EXEC.*`, and `TX_MEM.*`: transactional synchronization and TSX abort/commit diagnostics.
- `MACHINE_CLEARS.MEMORY_ORDERING`: memory-ordering machine-clear event with `Errata: SKL089`.

Normal fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `PEBS`, `MSRIndex`, `MSRValue`, `Data_LA`, `Errata`, descriptions, and sample defaults.

## Control flow and integration

Perf exposes these descriptors as Skylake aliases. Load-latency threshold events require programming the PEBS load-latency extra register through `MSRIndex` `0x3F6`, while offcore-response events require programming `0x1a6`/`0x1a7`. Transactional events use ordinary event encodings but are only meaningful when the processor and kernel expose the relevant TSX/HLE behavior.

The file integrates with memory-bound top-down analysis and with lower-level troubleshooting. Users can combine `CYCLE_ACTIVITY.*` stall signals, `MEM_TRANS_RETIRED.*` latency thresholds, and `OFFCORE_RESPONSE.*` supplier/snoop filters to identify whether stalls are due to local DRAM, snoop/coherency behavior, or transactional aborts.

## State and persistence behavior

The file has no mutable state. Runtime state lives in PMU counters, extra MSR filters, PEBS records with data addresses for eligible events, and perf's scheduling state. Hardware and kernel capabilities determine which descriptors can be used at measurement time.

## Dependencies

Dependencies include Skylake PMU definitions, perf's parser for extra MSR fields, kernel support for PEBS load-latency sampling, offcore response filtering, TSX/HLE event exposure, and CPU model selection. The load latency events also rely on memory-latency threshold semantics encoded in the `MSRValue` field.

## Risks and maintenance notes

Offcore response encodings are repetitive and high risk. The `.L3_MISS`, `.L3_MISS_LOCAL_DRAM`, `.SNOOP_NON_DRAM`, and related variants differ by bitmask combinations; a wrong `MSRValue` can produce plausible but wrong measurements.

TSX/HLE events can be confusing on systems where transactional memory is disabled by microcode, BIOS, kernel mitigations, or virtualization. The aliases may still exist as metadata but produce unsupported or zero-like behavior in practice.

`MACHINE_CLEARS.MEMORY_ORDERING` carries `SKL089`, so consumers should preserve the errata tag. Load latency threshold events depend on PEBS/data-address support and privilege settings; they should be tested separately from ordinary counting events.

## Test signals

Static checks should verify JSON validity, all 131 event records, valid `MSRIndex`/`MSRValue` pairs, and unique `EventName` values within the file. Runtime smoke tests should cover a `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` precise event, one `OFFCORE_RESPONSE.DEMAND_DATA_RD.L3_MISS_LOCAL_DRAM.*` alias, one `CYCLE_ACTIVITY.*` event, and at least one TSX/HLE alias with expected behavior documented when TSX is unavailable.
