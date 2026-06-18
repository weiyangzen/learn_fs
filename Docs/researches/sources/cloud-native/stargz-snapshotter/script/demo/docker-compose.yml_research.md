# sources/cloud-native/stargz-snapshotter/script/demo/docker-compose.yml

Purpose: Docker Compose stack for interactive containerd/stargz snapshotter demo.
Important APIs/types/functions: declarative configuration keys include privileged `containerd_demo`, FUSE mount, repo and data volumes, local registry service. There are no functions, but the keys are consumed by containerd, CRI-O, Podman, stargz-store, or systemd depending on the file.
Control flow: loaded by the relevant daemon at startup or by a test script that copies the file into `/etc` before restarting services.
State and persistence: persists runtime daemon configuration, storage roots, registry policy, or service startup behavior on the test node/container.
Dependencies and integration points: Pairs with `demo/init.sh` and `demo/run.sh` to run containerd plus snapshotter in a disposable container.
Risks: Misconfiguration can silently disable lazy pulling or weaken test security if copied outside controlled test containers.
Test signals: validated indirectly by the benchmark, CRI, demo, integration, or Podman scripts that boot services using this file.
