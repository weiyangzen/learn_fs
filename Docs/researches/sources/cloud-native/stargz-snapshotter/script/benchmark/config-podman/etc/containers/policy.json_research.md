# sources/cloud-native/stargz-snapshotter/script/benchmark/config-podman/etc/containers/policy.json

Purpose: Podman benchmark signature policy accepting test images without signature enforcement.
Important APIs/types/functions: declarative configuration keys include JSON `default` policy with `insecureAcceptAnything`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Consumed by containers/image inside the Podman benchmark container.
Risks: Intentionally insecure and suitable only for benchmark/test environments.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
