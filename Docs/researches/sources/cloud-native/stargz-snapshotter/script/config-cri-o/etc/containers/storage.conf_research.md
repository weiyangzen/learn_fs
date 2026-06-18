# sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/containers/storage.conf

Purpose: CRI-O storage config using overlay plus stargz-store as an additional layer store.
Important APIs/types/functions: declarative configuration keys include `driver`, `graphroot`, `runroot`, and `additionallayerstores`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Mounted into CRI-O test nodes so lazy layers can be served from `/var/lib/stargz-store/store:ref`.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
