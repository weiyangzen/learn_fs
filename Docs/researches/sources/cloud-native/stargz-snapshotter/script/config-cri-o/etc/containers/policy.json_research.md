# sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/containers/policy.json

Purpose: CRI-O test image policy accepting unsigned images.
Important APIs/types/functions: declarative configuration keys include JSON default policy `insecureAcceptAnything`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Installed into CRI-O test images for controlled local registry pulls.
Risks: Intentionally insecure outside isolated tests.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
