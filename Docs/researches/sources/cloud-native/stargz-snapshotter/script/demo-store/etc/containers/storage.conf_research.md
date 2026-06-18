# sources/cloud-native/stargz-snapshotter/script/demo-store/etc/containers/storage.conf

Purpose: Demo-store Podman storage config with stargz additional layer store.
Important APIs/types/functions: declarative configuration keys include overlay storage roots and `additionallayerstores`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Allows Podman to consume layers mounted by stargz-store.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
