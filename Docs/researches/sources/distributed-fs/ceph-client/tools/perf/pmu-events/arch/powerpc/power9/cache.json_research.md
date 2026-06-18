# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/cache.json

## Purpose

This file contributes 21 POWER9 core PMU events to the `cache` topic. The contents are broader than simple cache-hit counters: they include completion stalls attributed to load misses and load miss queue pressure, instruction-cache reload sources, marked-load reload latency, branch misprediction completion, threshold events, and a thread-concurrency instruction counter. All event names and event codes are unique within the file.

## APIs, types, and schema

Each array entry uses the event schema consumed by `jevents.py`: `EventName`, `EventCode`, and `BriefDescription`. The generated `JsonEvent` stores the lower-case event name, `default_core` PMU target, normalized description, and `event=<code>` encoding. This file contains no metrics; it exposes raw events that can be selected directly by perf and referenced by POWER9 metric formulas in `metrics.json`.

## Control flow and integration

`arch/powerpc/mapfile.csv` maps POWER9 PVRs to the `power9` directory. The perf build includes this JSON with the other POWER9 files, then `jevents.py` sorts and emits compact PMU event rows into `pmu-events.c`. These entries integrate with the generated POWER9 table used by perf listing, raw event lookup, and metric expression resolution. They also provide raw inputs for higher-level CPI and cache/memory-source metrics.

## State, persistence, and dependencies

The file is source data only; runtime state lives in perf's generated tables and the kernel PMU counters. It depends on the POWER9 PMU event schema, valid hexadecimal event encodings, and consistent naming with metric expressions such as `PM_BR_MPRED_CMPL`, `PM_CMPLU_STALL_FXLONG`, and `PM_CMPLU_STALL_LMQ_FULL`.

## Risks and test signals

Risks include topic mismatch, event-code mistakes, or descriptions that imply a different scope than the hardware counter actually measures. Several entries describe shared core behavior or marked-instruction latency, so consumers can misinterpret per-thread versus core-wide counts. Test signals include JSON parsing, a successful `pmu-events.c` generation, no duplicate event assertions, and metric tests proving any formulas that use these event names still parse and resolve.
