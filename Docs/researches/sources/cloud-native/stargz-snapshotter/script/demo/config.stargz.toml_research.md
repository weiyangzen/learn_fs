# sources/cloud-native/stargz-snapshotter/script/demo/config.stargz.toml

Purpose: Standalone snapshotter demo config enabling metrics, IPFS, direct directory cache, and relaxed restart handling.
Important APIs/types/functions: declarative configuration keys include `metrics_address`, `disable_verification`, `ipfs`, resolver mirror, `[directory_cache] direct`, and `[snapshotter] allow_invalid_mounts_on_restart`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Loaded by `containerd-stargz-grpc` in the demo environment.
Risks: Disables verification, so it is suitable for demo experimentation only.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
