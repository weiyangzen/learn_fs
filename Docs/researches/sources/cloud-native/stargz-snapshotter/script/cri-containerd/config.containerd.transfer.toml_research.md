# sources/cloud-native/stargz-snapshotter/script/cri-containerd/config.containerd.transfer.toml

Purpose: Containerd CRI config enabling stargz both as snapshotter and transfer-service unpack target.
Important APIs/types/functions: declarative configuration keys include CRI snapshotter, transfer `unpack_config` entries, and stargz proxy plugin export `enable_remote_snapshot_annotations`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Used when `TRANSFER_SERVICE=true` in CRI containerd tests to cover containerd transfer service paths.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
