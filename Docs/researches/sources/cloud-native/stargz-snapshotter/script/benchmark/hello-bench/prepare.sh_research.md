# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/prepare.sh

Purpose: Prepares benchmark image variants in a target repository before timing runs.
Important APIs/types/functions: environment variables `DISABLE_ESTARGZ`, paths to `hello.py` and `reboot_containerd.sh`; no reusable shell functions.
Control flow: validates arguments, starts plain containerd without stargz, then runs `hello.py --op=prepare` for selected images.
State and persistence: pushes legacy, eStargz, no-optimize, and zstdchunked image tags to the requested registry via `hello.py`.
Dependencies and integration points: depends on containerd/ctr-remote/nerdctl/crane availability inside the benchmark container.
Risks: argument expansion uses unquoted image lists; registry side effects are persistent and require credentials/environment to be correct.
Test signals: used as a setup step for benchmark runs; failures surface as missing target images.
