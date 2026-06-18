# sources/cloud-native/stargz-snapshotter/script/demo-store/docker-compose.yml

Purpose: Docker Compose environment for interactive Podman/stargz-store demo.
Important APIs/types/functions: declarative configuration keys include service build target `podman-base`, privileged mode, FUSE mount, repo/storage volumes, and local `registry2`. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Used with `demo-store/run.sh` to demonstrate Podman additional layer store behavior.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
