# sources/control-plane/juicefs-csi-driver/.github/workflows/dashboard-image.yaml

## Purpose
This manually dispatched workflow builds and pushes the CSI dashboard image, optionally using an operator-provided dashboard image tag.

## Important Jobs and Steps
The `publish-image` job checks out full history, installs pnpm 9, builds the dashboard UI via `make dashboard-dist`, logs into Docker Hub with `DOCKERHUB_FUSE_ACCESS_TOKEN`, sets up QEMU and Buildx, then runs `make -C docker dashboard-buildx` with `DASHBOARD_TAG` from workflow input. It opens an upterm session on failure.

## Control Flow
The workflow only runs on `workflow_dispatch`. Steps are linear; image publishing depends on successful UI build and Docker login.

## State and Persistence Behavior
The workflow publishes Docker images to external registries through Docker Hub credentials and whatever registry logic exists in the Docker Makefile. It does not write repository state.

## Dependencies and Integration Points
It integrates with `dashboard-ui-v2`, the root `Makefile`, `docker/dashboard.Dockerfile`, and Docker Buildx multi-platform build targets.

## Risks
It relies on a personal-looking Docker Hub username and secret. Failure debug via upterm exposes a live shell for up to 60 minutes and should be considered privileged. Because it is manual, it does not protect PRs by itself.

## Test Signals
Success indicates the dashboard UI can be built into a publishable image. Runtime dashboard behavior is not exercised.
