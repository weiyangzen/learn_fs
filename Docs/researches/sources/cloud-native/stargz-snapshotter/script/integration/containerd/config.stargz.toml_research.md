# sources/cloud-native/stargz-snapshotter/script/integration/containerd/config.stargz.toml

Purpose: Integration-test config for standalone stargz snapshotter.
Important APIs/types/functions: declarative configuration keys include metadata store, IPFS enablement, FUSE passthrough, blob retries/checking, and registry mirror. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Copied into integration test image and modified by `integration/test.sh` for metadata/fuse variants.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
