# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/run.sh

Purpose: Runs randomized benchmark samples across legacy, eStargz no-prefetch, eStargz, and zstdchunked modes.
Important APIs/types/functions: mode constants, `cleanup`, `output`, and `measure`; env `BENCHMARK_RUNTIME_MODE`, `BENCHMARK_SAMPLES_NUM`, `BENCHMARK_PROFILE`.
Control flow: selects containerd or Podman reboot script, prints host specs, randomizes image/mode workload order per sample, reboots runtime per workload, runs `hello.py --op=run`, checks remote snapshot logs for lazy modes, and emits JSON array fragments prefixed by `BENCHMARK_OUTPUT:`.
State and persistence: creates temporary workload/log files and `/tmp/hello-bench-output`; repeatedly clears runtime state through reboot scripts.
Dependencies and integration points: depends on `script/util/utils.sh` for `check_remote_snapshots`, the `hello.py` runner, and benchmark configs.
Risks: `sort -R` creates nondeterministic order by design; shell word splitting of image lists requires simple image names; one bad workload exits the entire run.
Test signals: consumed by `script/benchmark/test.sh`, which captures and formats its output.
