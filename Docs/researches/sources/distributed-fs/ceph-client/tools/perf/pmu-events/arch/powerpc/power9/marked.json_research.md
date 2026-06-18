# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/marked.json

## Purpose

This POWER9 file defines 125 PMU events centered on marked-instruction sampling, marked loads/stores, marked branch behavior, marked translation reloads, and related stall or cache-source attribution. It also includes unmarked supporting events such as radix page-walk cache reloads and data or instruction reload sources. The file is a key source for latency and attribution workflows because marked events let perf correlate selected sampled operations with memory, branch, or completion behavior.

## APIs, types, and schema

Each entry is a raw event object with `EventName`, `EventCode`, and `BriefDescription`. `jevents.py` parses the entries into `JsonEvent` objects, converts event codes to generated `event=...` strings, and emits compact event metadata. No metric formulas are declared here, but many entries provide raw event names used by POWER9 metrics and user-authored perf commands.

## Control flow and integration

The file participates in the normal POWER9 directory generation path. The generator reads all model JSON files, assigns the file-derived topic, normalizes names, checks duplicate event names within each generated PMU table, and stores strings in a shared compact string table. The generated table is linked through `libpmu-events.a` and used by perf at runtime when the current processor matches the POWER9 mapfile pattern.

## State, persistence, and dependencies

The file has no mutable state. It persists as PMU metadata and feeds generated code. It depends on the POWER9 PMU's marked-event semantics, sampling support, event-code accuracy, and naming stability across metric expressions and perf user interfaces.

## Risks and test signals

Marked events are easy to misuse because counts can represent sampled or marked subsets rather than all operations. Several descriptions also distinguish radix PTE reloads from PDE reloads, local versus remote cache hierarchy, and completion versus dispatch timing. Regression tests should include `jq empty`, `jevents.py` generation, duplicate-event detection, metric parse tests for formulas referencing marked names, and hardware validation of representative marked load, marked store, marked branch, and marked translation events.
