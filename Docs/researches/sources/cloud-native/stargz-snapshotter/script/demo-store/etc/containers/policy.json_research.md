# sources/cloud-native/stargz-snapshotter/script/demo-store/etc/containers/policy.json

Purpose: Demo-store containers/image policy accepting test images.
Important APIs/types/functions: declarative configuration keys include JSON default `insecureAcceptAnything`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Copied into the demo container by `demo-store/run.sh`.
Risks: Intentionally insecure and demo-only.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
