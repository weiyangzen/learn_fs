# sources/cloud-native/stargz-snapshotter/script/podman/config/containers.conf

Purpose: Rootless Podman config selecting slirp4netns for networking.
Important APIs/types/functions: declarative configuration keys include `[network] default_rootless_network_cmd`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Installed in the podman-rootless test image so rootless containers can run with expected networking.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
