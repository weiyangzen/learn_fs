# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/pipeline.json

## Purpose

This POWER9 file defines 106 pipeline-oriented PMU events. It includes execution-unit busy and idle counters, IERAT and DERAT reloads, marked load misses, PMC overflow controls, completion stalls, data-source attribution for marked loads, PTEG reload sources, completed instructions, vector/scalar unit activity, dispatch behavior, and other pipeline flow signals. The file is important for CPI breakdown and bottleneck analysis.

## APIs, types, and schema

The file uses the raw event schema: `EventName`, `EventCode`, and `BriefDescription`. `jevents.py` creates `JsonEvent` objects, converts event codes, assigns descriptions, and emits compact C rows. No metric objects are declared in this file, but many events are building blocks for the POWER9 `metrics.json` CPI, execution-unit, translation, and memory formulas.

## Control flow and integration

The file is selected as part of the POWER9 model directory by the PowerPC mapfile. `pmu-events/Build` includes it in JSON inputs; `jevents.py` adds its events to the generated POWER9 table and validates against duplicate generated names. At runtime, perf exposes the lower-case event names and resolves formulas that reference the original `PM_*` event symbols.

## State, persistence, and dependencies

The file is static source metadata with generated C as the build artifact. It depends on POWER9 counter encoding, kernel PMU support, and stable names for metric references. Because pipeline events often count cycles, completion slots, or marked subsets, correct interpretation depends on workload context and perf aggregation mode.

## Risks and test signals

Risks include misclassifying events as pipeline-only when they reflect translation or memory hierarchy behavior, formula breakage from renames, and hardware semantic mismatches for marked or per-slice counters. Test signals include JSON validation, successful perf PMU event generation, duplicate-name checks, metric parser coverage, and on-hardware checks of representative completion, execution-unit, instruction-completion, and marked-load events.
