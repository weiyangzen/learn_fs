# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/test/test_soc/cpu/metrics.json

## Purpose
Provides synthetic perf metric fixtures for expression parsing, metric dependency resolution, grouping, escaped event names, helper functions, cycles in metric references, and bandwidth-style formulas.

## APIs, Types, and Functions
The file contains 15 metric records with `MetricName`, `MetricExpr`, and optional `MetricGroup`. It defines simple reciprocal metrics (`CPI` as `1 / IPC`), direct event formulas (`IPC`), complex SMT arithmetic, escaped event names like `l1d\\-loads\\-misses`, derived cache metrics using `max()` and `d_ratio()`, cyclic references (`M1` and `M2`), self-reference (`M3`), and `L1D_Cache_Fill_BW` using `duration_time`.

## Control Flow, State, and Persistence
At generation time `jevents.py` parses each expression with the perf metric parser and writes generated metric metadata. At runtime in tests, perf resolves metric references and event names to exercise dependency handling. The cyclic metrics are deliberate fixtures for validation paths rather than usable production formulas.

## Dependencies and Integration
Depends on `tools/perf/pmu-events/metric.py`, `metric_test.py`, and the PMU event test harness. It also relies on known fixed event rewrites in `jevents.py` for names such as `inst_retired.any` and `cpu_clk_unhalted.thread`.

## Risks and Test Signals
Risks include accidentally accepting cyclic metrics in production paths, breaking escaped hyphen parsing, or changing helper-function semantics without updating fixtures. Test signals are metric parser unit tests, generated output comparisons, and explicit failures or diagnostics for cyclic/self-referential metrics.
