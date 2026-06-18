# sources/cloud-native/stargz-snapshotter/script/podman/config/podman-rootless-stargz-store.service

Purpose: User systemd unit for rootless stargz-store under Podman.
Important APIs/types/functions: declarative configuration keys include `ExecStart` via `podman unshare stargz-store`, root/address/store paths under `%h`, `ExecStopPost`, restart policy. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Started by `test-podman-rootless.sh` before rootless Podman lazy-pull tests.
Risks: Pipes through `cat` as a workaround; rootless mount cleanup can fail if store is busy.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
