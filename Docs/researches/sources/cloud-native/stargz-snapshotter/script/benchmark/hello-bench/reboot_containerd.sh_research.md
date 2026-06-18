# sources/cloud-native/stargz-snapshotter/script/benchmark/hello-bench/reboot_containerd.sh

Purpose: Resets and restarts the containerd benchmark environment with or without stargz lazy pulling.
Important APIs/types/functions: `retry`, `kill_all`, and `cleanup`; env flags `DISABLE_PREFETCH`, `DISABLE_ESTARGZ`, `LOG_FILE`.
Control flow: kills existing daemons, removes containerd and snapshotter state, rewrites `noprefetch`, optionally starts `containerd-stargz-grpc`, then starts containerd and waits for `ctr`/`ctr-remote version`.
State and persistence: destructively clears `/var/lib/containerd` and `/var/lib/containerd-stargz-grpc`; may append snapshotter logs to a provided file.
Dependencies and integration points: integrates benchmark configs, system daemons, FUSE mounts, and `ctr-remote` fallback to `ctr`.
Risks: uses broad `ps|grep|kill -9` matching and `rm -rf` on daemon roots, so it must only run in disposable benchmark nodes.
Test signals: benchmark modes rely on it to isolate each workload and validate daemon readiness.
