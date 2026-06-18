# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/memory.json

## Purpose

`memory.json` defines 240 Broadwell core PMU events for memory-related profiling. It covers hardware lock elision and restricted transactional memory retire/abort accounting, memory-ordering machine clears, PEBS sampled load-latency thresholds, misaligned loads/stores, offcore response filters, and TSX memory abort causes. Its largest family is `OFFCORE_RESPONSE`, with 201 combinations of request type, cache outcome, local DRAM outcome, and snoop response.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects consumed by perf's `pmu-events` generator. Important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Memory-specific rows also use `MSRIndex` and `MSRValue` for offcore response and load-latency filter programming, `PEBS` and `Data_LA` for precise load-latency sampling, and `Errata` for Broadwell errata annotations such as `BDM100, BDM35`.

Important event families include `HLE_RETIRED.*`, `RTM_RETIRED.*`, `TX_EXEC.*`, `TX_MEM.*`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, `MISALIGN_MEM_REF.*`, `MACHINE_CLEARS.MEMORY_ORDERING`, and `OFFCORE_RESPONSE.*`. The offcore rows use event codes `0xB7, 0xBB` and MSRs `0x1a6,0x1a7`; this lets perf program either offcore response register while exposing one logical event name.

## Control Flow and Data Flow

There is no runtime control flow in the file. At build time, perf's PMU event tooling reads the JSON catalog and emits static event tables into generated `pmu-events.c`. At runtime, perf resolves a requested event name, maps it to event-select fields and any auxiliary MSR programming, then asks the kernel PMU driver to configure the hardware counters. For load-latency rows, the data path includes PEBS sampling and an MSR latency threshold. For offcore rows, the `MSRValue` encodes request/source/snoop filters and the hardware counts matching offcore responses.

## State and Persistence Behavior

The file persists static hardware metadata in the source tree. It does not store runtime state, user state, or counter values. The only persistent effects are generated build artifacts derived from the JSON table and installed perf event metadata. Sampling defaults in `SampleAfterValue` influence perf's default period if the event is sampled.

## Dependencies and Integration Points

This catalog depends on the Broadwell PMU architectural event definitions, model-specific offcore response encodings, TSX/HLE semantics, PEBS support, and Broadwell errata. It integrates with `tools/perf/pmu-events` JSON parsing, generated `pmu-events.c`, `perf list`, `perf stat`, `perf record`, perf's metric parser, and the kernel PMU implementation that accepts event select, umask, counter constraints, PEBS, and extra MSR programming.

## Risks and Edge Cases

The highest-risk rows are the offcore and PEBS load-latency entries because a wrong `MSRValue`, `MSRIndex`, or counter constraint silently measures a different traffic class. `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` is constrained to counter `3`, uses PEBS level `2`, and depends on load latency MSR programming; relaxing those constraints would create invalid or misleading profiles. Offcore events have dense, repetitive names, so copy/paste mistakes can swap request classes such as demand reads, RFOs, prefetches, code reads, and writebacks. TSX/HLE events are useful only where TSX is available and enabled; on affected systems, firmware or microcode policy may disable TSX even on a Broadwell-family CPU.

## Test Signals

Useful validation signals are successful JSON parsing, successful `pmu-events` generation, event visibility in `perf list` on a Broadwell matching model, and basic `perf stat -e` acceptance for representative rows from each family. For offcore rows, compare generated encodings against Intel tables and smoke-test both `0xB7` and `0xBB` programming paths. For PEBS load-latency rows, `perf record` should accept the event and produce precise samples with data address/latency support where the kernel and hardware expose it.
