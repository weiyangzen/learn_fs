# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arm64_metrics.py

Purpose: command-line generator for ARM64 perf extra metric JSON. It loads an ARM64 vendor/model event directory and emits either metric definitions or metric-group descriptions. In the current implementation it emits the shared privilege-level cycle breakdown from `common_metrics.Cycles()`.

Important APIs/types/functions: imports `argparse`, `os`, `JsonEncodeMetric`, `JsonEncodeMetricGroupDescriptions`, `LoadEvents`, `MetricGroup`, and `Cycles`. The public executable entry point is `main()`. Inside `main`, nested `dir_path(path)` validates that the supplied events root is a directory for `argparse`. Command-line API: optional `-metricgroups`, positional `vendor`, positional `model`, and positional `events_path`. The script constructs `directory = f"{events_path}/arm64/{vendor}/{model}/"`, calls `LoadEvents(directory)`, wraps `Cycles()` in a root `MetricGroup("", [...])`, and prints either metric JSON or group-description JSON.

Control flow: module import initializes `_args = None`. When run as a script, `main()` builds and parses the CLI, validates the root directory, loads model event names for metric validation, constructs the metric tree, then chooses one of two JSON encoders based on `_args.metricgroups`. Output goes to stdout for the build system to redirect into `extra-metrics.json` or `extra-metricgroups.json`.

State and persistence: `_args` is a module-global copy of parsed arguments, but all generated content is derived from source JSON files and printed to stdout. Persistent output is created by the Make/Build rule that redirects stdout, not by this script opening output files.

Dependencies: depends on `metric.py` for event loading, metric tree types, validation, and JSON encoding; depends on `common_metrics.py` for the shared `Cycles()` metric group; depends on a valid `pmu-events/arch/arm64/<vendor>/<model>/` directory. The build file invokes it for ARM model directories, excluding CMN directories, when `JEVENTS_ARCH` includes `arm64` or `all`.

Integration points: integrated by `tools/perf/pmu-events/Build` rules for `ARM_METRICS` and `ARM_METRICGROUPS`. The generated JSON is later consumed by perf's pmu-events generation and surfaced as extra ARM metrics. The `LoadEvents` call also validates that `Event("cpu\\-cycles:...")` references used by `Cycles()` are accepted by the loaded model event set or by the built-in generic events in `metric.py`.

Risks: `dir_path` validates only the root `events_path`, not the constructed vendor/model directory; a wrong vendor/model can fail later in `LoadEvents`. The script currently emits only cycle metrics, so ARM64 extra metrics are intentionally sparse. Because it prints to stdout, warnings or debug output added later would corrupt generated JSON. The global `_args` is harmless for script usage but makes repeated in-process calls stateful.

Test signals: run with a known ARM64 events tree and validate JSON parses for both default and `-metricgroups` modes. Unit-style checks can monkeypatch a small events directory and assert the output contains `lpm_cycles_total`, `lpm_cycles_user`, `lpm_cycles_kernel`, `lpm_cycles_guest`, and group description `lpm_cycles`. Build integration is covered by the `ARM_METRICS` and `ARM_METRICGROUPS` targets.
