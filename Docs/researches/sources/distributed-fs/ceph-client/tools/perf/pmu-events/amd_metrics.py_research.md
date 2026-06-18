<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/amd_metrics.py -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/amd_metrics.py

## Purpose
This Python script generates AMD Zen perf metric JSON and metric-group description JSON for the `tools/perf/pmu-events` build. It builds higher-level metrics from AMD raw events, common cycle metrics, and perf software/MSR events, then prints either metric rows or metric group descriptions. The source was read as a complete 493-line file.

## Important APIs, Types, and Functions
Top-level inputs are argparse options `-metricgroups`, `model`, and `events_path`; globals include `_zen_model`, `interval_sec`, `ins`, `cycles`, and SMT-aware `smt_cycles`. Metric builders are `AmdBr()`, `AmdCtxSw()`, `AmdDtlb()`, `AmdItlb()`, `AmdLdSt()`, `AmdUpc()`, `Idle()`, `Rapl()`, and `UncoreL3()`. The script uses `Event`, `Metric`, `MetricGroup`, `Select`, `Literal`, `d_ratio()`, `max()`, `LoadEvents()`, `JsonEncodeMetric()`, and `JsonEncodeMetricGroupDescriptions()` from the local PMU metric framework.

## Control Flow, State, and Persistence
`main()` validates the event-tree directory, loads the selected `x86/<model>/` JSON files, derives `_zen_model` from names such as `amdzen1`, and builds one root `MetricGroup` containing all AMD metric groups. Individual builders create nested groups for branches, context switches, DTLB, ITLB, load/store throughput, uops per cycle, privilege-level cycles, idle time, package power, and L3 behavior. Several branches are model-sensitive: DTLB metrics are skipped for Zen 4 and newer, coalesced-page events appear for Zen 2 and newer, and some L1 TLB access formulas are Zen 1-3 only. The script persists nothing itself; build rules redirect stdout into generated `metrics.json` or `metricgroups.json` files.

## Dependencies and Integration Points
The `Build` file invokes this script for each `pmu-events/arch/x86/amdzen*` directory. It depends on local modules `metric.py` and `common_metrics.py`, and on the event names present in the AMD Zen JSON inputs. `LoadEvents()` validates referenced event names across the selected model tree, while the generated JSON is later parsed by `jevents.py` into perf's generated `pmu-events.c` tables. Runtime integration is through `perf stat -M`, metric groups, MSR PMUs (`msr/mperf/`, `msr/tsc/`), RAPL `power/energy-pkg/`, and AMD core/uncore PMU events.

## Risks and Test Signals
Risks include event-name drift across Zen generations, model gating that silently drops or includes invalid formulas, SMT scaling assumptions in `smt_cycles`, division by unavailable or zero-count events, RAPL scaling accuracy, and metric semantics changing when AMD event aliases change. Test signals include running the script for every `amdzen*` model, comparing generated JSON diffs, executing `metric_test.py`, running `jevents.py`, checking `perf list --metrics` for generated names, and smoke-testing representative `perf stat -M lpm_*` groups on matching AMD hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/amd_metrics.py -->
