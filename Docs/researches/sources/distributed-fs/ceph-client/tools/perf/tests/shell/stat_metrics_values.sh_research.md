## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_metrics_values.sh

Purpose: runs Intel metric value validation rules through a Python validator.
Important behavior: requires GenuineIntel CPU, discovers Python, sets validator and rule JSON paths, and tests each `/sys/bus/event_source/devices/cpu_*` cputype.
Control flow: for each cputype it invokes `perf_metric_validation.py` with workload `perf bench futex hash -r 2 -s`, an output directory, rules, and cputype; nonzero return prints an error notice and final exit returns the last validator status.
State and persistence: creates a temp output directory and removes it inside the loop.
Dependencies and integration: Intel PMU metrics, Python validation helper, rule JSON, and perf bench futex.
Risks: `tmpdir` is removed after the first iteration, so later validator invocations may depend on recreating output internally; final `ret` is undefined if no `cpu_*` dirs exist.
Test signals: validator exit status and generated validation artifacts on failure.
