# sources/distributed-fs/ceph-client/tools/perf/pmu-events/common_metrics.py

Purpose: defines shared perf metric groups that are reused by architecture-specific metric generators. The current file exposes `Cycles()`, a privilege-level cycle breakdown metric group used by ARM64, Intel, and AMD metric-generation scripts.

Important APIs/types/functions: imports `d_ratio`, `Event`, `Metric`, and `MetricGroup` from `metric.py`. `Cycles() -> MetricGroup` creates three event expressions: `cyc_k = Event("cpu\\-cycles:kHh")` for kernel/hypervisor-side host cycles excluding user and guest, `cyc_g = Event("cpu\\-cycles:G")` for guest cycles excluding host, and `cyc_u = Event("cpu\\-cycles:uH")` for user host cycles excluding kernel, hypervisor, and guest. It sums them into `cyc` and returns a `MetricGroup("lpm_cycles", [...])` containing four metrics: total cycles plus user, kernel, and guest percentages using `d_ratio(part, cyc)` with scale `100%`.

Control flow: no top-level work beyond imports. Calling `Cycles()` constructs expression objects, uses operator overloading from `metric.Expression` subclasses to sum events, creates metrics, and returns a metric group with description `cycles breakdown per privilege level (users, kernel, guest)`.

State and persistence: no module state and no persistence. The returned metric objects are later serialized by architecture-specific scripts through `JsonEncodeMetric` or `JsonEncodeMetricGroupDescriptions`.

Dependencies: tightly depends on `metric.py` expression semantics: `Event` validates event names/modifiers, `d_ratio` emits a perf metric expression, `Metric` normalizes scale units, and `MetricGroup` propagates metric group names. It also depends on perf's event modifier syntax for `cpu-cycles` privilege filters (`kHh`, `G`, `uH`) remaining valid across supported architectures.

Integration points: imported by `arm64_metrics.py`, `intel_metrics.py`, and `amd_metrics.py`. The build system lists it in `GEN_METRIC_DEPS`, so changes trigger regeneration of architecture extra metric JSON. Its metric names are part of the generated user-facing perf metric namespace: `lpm_cycles_total`, `lpm_cycles_user`, `lpm_cycles_kernel`, and `lpm_cycles_guest`.

Risks: event modifier mistakes would change privilege accounting without obvious JSON syntax failures. The denominator `cyc` is the sum of three filtered events; if an architecture or perf mode treats host/guest/hypervisor filters differently, percentages may be misleading. Renaming metric names or the `lpm_cycles` group can break users or tests that rely on stable metric aliases. Division-by-zero behavior is delegated to perf's `d_ratio` implementation.

Test signals: direct serialization test through an architecture generator should produce four metric objects with the expected names, group `lpm_cycles`, `MetricExpr` values containing the three `cpu\\-cycles` filtered events, and scale units `1cycles`/`100%` as normalized by `Metric`. Build-level signal is regeneration of extra metrics for ARM64, Intel, and AMD without validation errors.
