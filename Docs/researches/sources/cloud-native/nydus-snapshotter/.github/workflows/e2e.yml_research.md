# sources/cloud-native/nydus-snapshotter/.github/workflows/e2e.yml

Purpose: integration tests for cgroup v1 and v2 environments.

Flow: triggers on main pushes, version tags, PRs to main, daily schedule, and manual dispatch. It runs `make integration` on Ubuntu 22.04 for cgroups v1 and Ubuntu 24.04 for cgroups v2 after registry login.

State/dependencies: relies on Docker, GitHub container registry credentials, Go setup, and integration Dockerfile/entrypoint behavior.

Integration points: validates real containerd/nydus-snapshotter/nydusd behavior across kernel cgroup modes.

Risks/tests: privileged container execution and external image availability are required. `TAG` is computed but not directly consumed by the shown commands.
