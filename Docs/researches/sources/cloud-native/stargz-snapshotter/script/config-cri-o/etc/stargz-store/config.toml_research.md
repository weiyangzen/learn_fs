# sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/stargz-store/config.toml

Purpose: Placeholder stargz-store config for CRI-O test images.
Important APIs/types/functions: declarative configuration keys include empty/comment-only config. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Scripts append resolver and metadata settings as needed before starting stargz-store.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
