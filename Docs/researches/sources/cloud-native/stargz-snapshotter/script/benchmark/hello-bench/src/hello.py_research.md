# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/src/hello.py

Purpose: Core benchmark driver for preparing optimized image variants and timing pull/create/start for a catalog of workloads.
Important APIs/types/functions: classes `RunArgs`, `Bench`, `BenchRunner`, `ContainerdController`, `PodmanController`; helpers `format_repo`, `genargs_for_optimization`, `tmp_copy`, and CLI `main`.
Control flow: parses CLI flags, chooses runtime controller, prepares images by copying/or optimizing to mode-specific tags, or runs benchmark iterations by pulling images, creating containers with command/stdio/wait-line strategies, starting them, recording elapsed times, cleaning up, and printing JSON rows with `BENCHMARK_OUTPUT:`.
State and persistence: uses a temporary directory for copied mounts, creates/pushes images in external registries, creates/removes runtime containers and images, and can write pprof output under `/tmp/hello-bench-output`.
Dependencies and integration points: integrates ctr/ctr-remote, nerdctl, crane, Podman, optimizer command flags, benchmark fixture files, and specific image command expectations.
Risks: many commands are shell-formatted strings with limited quoting; assertions abort on nonzero commands; wait-line loops can hang if stdout stalls; benchmark catalog versions are fixed and may age.
Test signals: covered by benchmark scripts rather than unit tests; output is post-processed by tools under `script/benchmark/tools`.
