# sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/systemd/system/stargz-store.service

Purpose: Systemd unit that starts stargz-store before CRI-O.
Important APIs/types/functions: declarative configuration keys include `After`, `Before`, `Type=notify`, `ExecStart`, `ExecStopPost`, and restart policy. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Ensures the additional layer store is mounted before `crio.service` starts.
Risks: Stop cleanup runs a direct `umount`; failures or busy mounts can leave state for later tests.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
