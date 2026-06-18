# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/transaction.json

## Purpose
Defines derived z17 perf metrics over CPU-M-CF event aliases. The metrics summarize transaction activity, CPI, problem-state ratio, L1 miss pressure, cache/memory sourcing percentages, finite-cache CPI components, and estimated TLB cost.

## APIs, Types, and Functions
This file contains 14 metric records rather than raw events. Each record uses `MetricName`, `MetricExpr`, and `BriefDescription`. Expressions use perf metric syntax with arithmetic, references to event aliases from `basic.json` and z17 `extended.json`, and guards such as `if has_event(TX_C_TEND) else 0`.

## Control Flow, State, and Persistence
At build time `jevents.py` parses `MetricExpr` through `metric.ParsePerfJson()` and stores the simplified metric formula in generated tables. At runtime perf resolves referenced event aliases, opens the required counters, computes formulas after sampling, and reports zero for guarded metrics when the leading event is unavailable.

## Dependencies and Integration
Depends heavily on event names from z17 `extended.json` (`TX_*`, `DCW_*`, `ICW_*`, `L1C_TLB2_MISSES`, `DTLB2_*`, `ITLB2_*`) and basic CPU-M-CF names such as `CPU_CYCLES`, `INSTRUCTIONS`, `L1I_DIR_WRITES`, and `L1D_DIR_WRITES`. It also depends on perf metric expression parsing, `has_event()`, division handling, and event scheduling constraints.

## Risks and Test Signals
Risks include division by zero when denominators such as `INSTRUCTIONS` or L1 directory writes are zero, guard conditions that check only one representative event while the expression needs many, and metric drift if referenced aliases are renamed. Good test signals are metric parser tests, `perf list --details` showing the formulas, `perf stat -M transaction,cpi,...` on z17, and negative tests on non-z17 systems confirming guarded metrics do not fail alias resolution.
