# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/other.json

## Purpose

`other.json` is a Snow Ridge X86 perf PMU event catalog for events that do not fit cleanly into the memory or pipeline group files. It defines bus-lock, interrupt, deprecated memory-bound stall aliases, and several offcore response (`OCR.*`) miscellaneous response/latency events for the `snowridgex` model.

The file is declarative event metadata. Runtime behavior is provided by the shared Linux `perf` PMU event parser, generated event tables, and X86 PMU programming logic.

## Important APIs, Types, and Data Shape

The file is a JSON array of 22 event objects using the perf PMU event schema. Important fields are:

- `EventName`: symbolic alias exposed to users, such as `BUS_LOCK.SELF_LOCKS`, `HW_INTERRUPTS.MASKED`, or `OCR.UC_RD.OUTSTANDING`.
- `EventCode` and `UMask`: raw programmable event encoding where applicable.
- `Counter`: all entries target general-purpose counters `0,1,2,3`.
- `EdgeDetect`: used by bus-lock count events that count accepted/self bus locks as edges.
- `Deprecated`: present on compatibility aliases for old bus-lock and C0-stall names.
- `MSRIndex` and `MSRValue`: used by OCR events that require offcore response MSR programming.
- `PublicDescription`, `BriefDescription`, and `SampleAfterValue`: user-facing and sampling metadata.

There are no `PEBS` entries in this file.

## Event Coverage

The file defines four main categories:

- `BUS_LOCK.*`: current aliases `BLOCK_CYCLES`, `LOCK_CYCLES`, and `SELF_LOCKS`, plus deprecated aliases `ALL`, `CYCLES_OTHER_BLOCK`, and `CYCLES_SELF_BLOCK`.
- `C0_STALLS.*`: three deprecated load-stall aliases that refer users to `MEM_BOUND_STALLS.LOAD_DRAM_HIT`, `LOAD_L2_HIT`, and `LOAD_LLC_HIT`.
- `HW_INTERRUPTS.*`: masked cycles, pending-and-masked cycles, and received interrupt count events.
- `OCR.*`: `ANY_RESPONSE` and `OUTSTANDING` variants for code reads, streaming writes, miscellaneous requests, prefetches, and uncached reads/writes.

The `OCR.*.OUTSTANDING` events use only `MSRIndex` `0x1a6` and encode latency-style counting with high-bit `MSRValue` values such as `0x8000000000000044` and `0x8000100000000000`.

## Control Flow and Integration

There is no executable control flow in the file. The effective flow is:

1. Perf discovers the file under `arch/x86/snowridgex`.
2. The event-table tooling parses each object and joins it with the Snow Ridge model event set.
3. User-facing tools expose the names through `perf list` and resolve them in `perf stat` or `perf record`.
4. For `BUS_LOCK.*`, perf programs event `0x63` with the appropriate umask and edge-detect flag where present.
5. For `HW_INTERRUPTS.*`, perf programs event `0xcb` with umasks `0x1`, `0x2`, or `0x4`.
6. For OCR entries, perf programs event `0XB7`, umask `0x1`, and the requested offcore response MSR value.

Deprecated entries remain part of resolution flow so old names can continue to resolve while pointing users toward newer aliases.

## State and Persistence Behavior

The file itself has no mutable state. Its content becomes persistent perf metadata after installation or build. The `Deprecated` flags, event names, and descriptions are persistent compatibility signals: changing them affects scripts, dashboards, and profiling documentation that rely on stable event aliases.

## Dependencies and Coupling

Dependencies include:

- The perf PMU event JSON schema.
- Snow Ridge PMU support for event codes `0x63`, `0xcb`, and `0XB7`.
- Offcore response MSRs `0x1a6` and `0x1a7` for OCR events.
- Shared perf handling for `EdgeDetect` and `Deprecated`.

The file is coupled to `pipeline.json` through deprecated `C0_STALLS.*` references to `MEM_BOUND_STALLS.*` names that are not defined in this file, and to `memory.json` through shared OCR request categories.

## Risks

- Deprecated aliases are still valid public names. Removing or renaming them can break existing perf command lines.
- `BUS_LOCK.ALL` has `Deprecated` and `EdgeDetect` but no `UMask`; parsers must tolerate event-specific defaults as represented in upstream event tables.
- OCR entries use uppercase `0XB7`, matching nearby Snow Ridge files but potentially surprising strict text validators.
- Long interrupt descriptions are surfaced to users; truncation or escaping issues in generated tables would reduce usability.
- The `OUTSTANDING` OCR entries use only `MSRIndex` `0x1a6`, unlike many `ANY_RESPONSE` entries that use both `0x1a6,0x1a7`. Validation should preserve this distinction.

## Test Signals

Useful validation signals include:

- `jq` parse and length checks; this file contains 22 event objects.
- Perf table generation for the Snow Ridge model.
- `perf list` checks for `BUS_LOCK.SELF_LOCKS`, `BUS_LOCK.ALL`, `HW_INTERRUPTS.PENDING_AND_MASKED`, `OCR.ALL_CODE_RD.OUTSTANDING`, and `OCR.UC_RD.OUTSTANDING`.
- Checks that six deprecated aliases remain marked deprecated.
- Checks that `EdgeDetect` is retained for `BUS_LOCK.ALL` and `BUS_LOCK.SELF_LOCKS`.
- OCR encoding tests that preserve `MSRIndex` differences between `ANY_RESPONSE` and `OUTSTANDING` events.
