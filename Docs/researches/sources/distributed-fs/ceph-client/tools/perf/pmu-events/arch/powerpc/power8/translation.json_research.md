# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/translation.json

## Purpose

This JSON file defines POWER8 translation-related core PMU events for Linux perf. It contains 29 event objects, all with unique `EventName` values, `EventCode` values, and descriptions. The events focus on data-side translation behavior: data ERAT misses by page size, DTLB misses by page size, general TLB misses, and PTEG reload sources for data-side page table entries. It is selected for POWER8-compatible processors through `arch/powerpc/mapfile.csv`, where POWER8 PVR patterns map to the `power8` model directory.

## APIs, types, and schema

The file is declarative data consumed by `tools/perf/pmu-events/jevents.py`. Each object maps into a `JsonEvent`: `EventName` becomes a lower-case perf event name, `EventCode` becomes the generated `event=...` encoding, `BriefDescription` becomes the short description, and `PublicDescription`, present in this file, becomes the long description unless it duplicates the short one. There are no functions or exported symbols in the JSON itself; its public API is the stable PMU-event schema expected by perf.

## Control flow and integration

During a perf build, `pmu-events/Build` includes JSON and CSV inputs under `pmu-events/arch`, then runs `jevents.py` to generate `pmu-events.c`. `jevents.py` loads the array with `json.load(..., object_hook=JsonEvent)`, normalizes descriptions, converts the event code with base auto-detection, and appends the entries to the model event table. At runtime, perf commands such as `perf list` and event selection resolve these generated entries through the PMU event tables for the matching PowerPC model.

## State, persistence, and dependencies

There is no runtime mutable state in this file. Its contents persist as source-controlled JSON and are compiled into generated C tables. It depends on valid JSON syntax, the perf PMU event schema, the POWER8 model mapping, and event names that match IBM POWER PMU documentation and kernel PMU encodings.

## Risks and test signals

The primary risks are incorrect event codes, ambiguous translation-source descriptions, or schema drift that prevents `JsonEvent` conversion. Because formulas do not reference this file directly, failures are most likely to appear as missing or misencoded `perf list` events rather than metric parse failures. Useful test signals are `jq empty` for syntax, a perf build that regenerates `pmu-events.c`, generated-table duplicate checks from `jevents.py`, and manual `perf list` verification on a POWER8 or compatible system.
