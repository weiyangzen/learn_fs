# sources/cloud-native/stargz-snapshotter/script/podman/test.sh

Purpose: Builds and runs the rootless Podman stargz-store test image.
Important APIs/types/functions: uses `check_remote_snapshots`, temp logs, and generated Dockerfile that runs `run_test.sh`.
Control flow: builds base podman-rootless image if needed, builds a node image containing `run_test.sh`, runs it privileged, captures logs, extracts remote snapshot JSON lines, and validates them.
State and persistence: creates temp context/log files and Docker images; pulls/runs public images inside the test container.
Dependencies and integration points: depends on Docker, podman-rootless Dockerfile stage, stargz-store service config, and utility log checker.
Risks: requires privileged Docker run even though testing rootless behavior; public registry availability is needed.
Test signals: top-level Podman rootless CI signal.
