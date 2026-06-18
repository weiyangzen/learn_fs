# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/other.json

## Purpose

`other.json` contains two miscellaneous Skylake PMU event descriptors that do not fit cleanly into the other category files. The events are `HW_INTERRUPTS.RECEIVED`, counting hardware interrupts received by the processor, and `MEMORY_DISAMBIGUATION.HISTORY_RESET`, counting memory-disambiguation history resets.

## Important schema/API surface

The two array entries use standard event descriptor fields:

- `HW_INTERRUPTS.RECEIVED`: event code `0xCB`, unit mask `0x1`, generic counters `0,1,2,3`, and descriptions for processor hardware interrupt receipt.
- `MEMORY_DISAMBIGUATION.HISTORY_RESET`: event code `0x09`, unit mask `0x1`, generic counters `0,1,2,3`, with a minimal matching description.

Both records include `EventName`, `EventCode`, `UMask`, `Counter`, descriptions, and `SampleAfterValue`. They do not need MSR filters, PEBS, errata tags, or metric groups.

## Control flow and integration

Perf loads these as ordinary Skylake event aliases. Selecting either event programs a generic counter using only the raw event code and unit mask. They integrate as low-level diagnostics: interrupts can explain OS noise or workload disruption, while memory-disambiguation resets can point to speculative load/store ordering behavior.

## State and persistence behavior

The file is static metadata with no mutable state. Runtime state is limited to PMU counter values gathered by perf.

## Dependencies

The descriptors depend on Skylake's core PMU encodings and perf's standard event JSON parser.

## Risks and maintenance notes

The descriptions are short, especially for `MEMORY_DISAMBIGUATION.HISTORY_RESET`; downstream documentation may need external Intel references for detailed interpretation. Because this category is miscellaneous, future additions should avoid becoming a dumping ground for events that would be better placed in pipeline, memory, or frontend files.

## Test signals

Static validation should check syntax, exactly two entries, and required fields. Runtime smoke tests can run `perf stat -e HW_INTERRUPTS.RECEIVED` and `perf stat -e MEMORY_DISAMBIGUATION.HISTORY_RESET` on Skylake hardware.
