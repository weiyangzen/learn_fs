# sources/cloud-native/stargz-snapshotter/script/config-cri-o/etc/containers/registries.conf

Purpose: CRI-O containers/image registry config enabling stargz-store auth helper.
Important APIs/types/functions: declarative configuration keys include `unqualified-search-registries` and `additional-layer-store-auth-helper`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Works with CRI-O, containers/image, and stargz-store helper for additional layer store access.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
