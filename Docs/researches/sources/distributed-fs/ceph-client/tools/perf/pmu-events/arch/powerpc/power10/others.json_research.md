# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/others.json

## Purpose

This file defines 14 miscellaneous POWER10 raw PMU events that do not fit cleanly into the pipeline, PMC, translation, or metric formula files. The events cover adjunct cycles and completions, instruction dispatch, load demand L1 miss, all L1 instruction-cache reloads, `isync` completion, load/store 32-byte finish slots, unaligned load/store finishes, strided prefetch conflict, and cycles blocked by a full instruction buffer.

## APIs, types, and schema

The file uses the raw PMU event JSON schema: each entry has `EventCode`, `EventName`, and `BriefDescription`. There is no `PublicDescription`. The stable API is the event name to event code mapping, for example `PM_ADJUNCT_CYC`, `PM_ADJUNCT_INST_CMPL`, `PM_INST_DISP`, `PM_LD_DEMAND_MISS_L1`, `PM_L1_ICACHE_RELOADED_ALL`, and `PM_NO_FETCH_IBUF_FULL_CYC`.

## Control flow and integration

Perf build tooling ingests these entries through `jevents.py`, emits them into generated event tables, and later resolves them when users run commands such as `perf stat -e PM_INST_DISP` or when metrics in `metrics.json` reference the same names. Several events are direct dependencies of derived POWER10 metrics, including load miss and instruction reload formulas.

## State and persistence

There is no runtime state. The persistent contract is the event-code mapping for POWER10. Event names become part of the generated PMU table and are consumed directly by users and indirectly by metrics. Event codes are unique within this file.

## Dependencies

Dependencies are the POWER10 PMU encoding, perf's event table generator, and metric expressions that reference these counters. The file integrates with the same architecture mapfile path that selects the POWER10 event directory for POWER processors.

## Risks

Because descriptions are brief and there is no `PublicDescription`, ambiguous events such as slot-specific `PM_LD0_32B_FIN` and `PM_LD1_32B_FIN` rely on hardware documentation for full meaning. Any mismatch between `EventCode` and actual POWER10 PMU encoding would silently produce wrong measurements. The miscellaneous grouping can make ownership and coverage reviews harder than category-specific files.

## Test signals

Run JSON validation, unique event-code and event-name checks, perf PMU generation, and runtime event-open checks on POWER10. Metrics that reference `PM_INST_DISP`, `PM_LD_DEMAND_MISS_L1`, and `PM_L1_ICACHE_RELOADED_ALL` are useful integration smoke tests.
