# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/frontend.json

## Purpose

This POWER9 file defines 71 frontend-adjacent PMU events. It covers instruction-side PTEG reload sources, dispatch and issue holds, instruction fetch pump-scope prediction, branch completion and synchronization markers, L1 instruction-cache reloads, and several load/store or data-source counters that interact with frontend or pipeline flow. Within the file all event names are unique and each event has an event code and short description.

## APIs, types, and schema

The file exports event metadata through the standard perf PMU JSON schema: `EventName`, `EventCode`, and `BriefDescription`. `JsonEvent` lower-cases the name for generated lookup, normalizes the description, assigns the default core PMU, and emits an `event=<hex>` string into the compact generated table. It contains no metric objects, but several event names are used by POWER9 derived metrics.

## Control flow and integration

The POWER9 model path is selected by the PowerPC mapfile. During build, `pmu-events/Build` includes this file in `SRC_JSON`; with an output directory it may copy it into the generated `pmu-events/arch` tree before invoking `jevents.py`. The generator adds the entries to the pending POWER9 event table, groups them by PMU name, and writes compact rows into `pmu-events.c`. Runtime consumers are perf event lookup, `perf list`, and metric expression evaluation.

## State, persistence, and dependencies

State is static source JSON plus generated C output. Dependencies include valid JSON, stable POWER9 counter encodings, kernel support for POWER9 PMU events, and consistency with formula references such as instruction-fetch, branch, and dispatch-stall metrics.

## Risks and test signals

Risks are split across hardware semantics and catalog consistency. Many counters include core-shared resources, marked events, or pump-scope speculation, so bad descriptions can lead to incorrect performance interpretation. Formula consumers can also break if event names are renamed. Test signals include JSON validation, a full perf build with `pmu-events.c` regeneration, metric parsing, duplicate-name assertions in `jevents.py`, and hardware spot checks for representative instruction-fetch, branch, and dispatch-hold events.
