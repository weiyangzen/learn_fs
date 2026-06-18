<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/docker-check.yml -->

# sources/distributed-fs/ipfs-kubo/.github/workflows/docker-check.yml


## Purpose
Pull-request/push Docker validation workflow for Kubo.


## Important APIs, Types, and Functions
Triggers on workflow_dispatch, pull_request excluding markdown-only changes, and pushes to master. It has lint and build jobs: hadolint, Dockerfile GO_VERSION guard, Buildx build using go.mod version, cache configuration, and docker run --version smoke test.


## Control Flow
The lint job validates Dockerfile quality and checks the default GO_VERSION ARG matches go.mod. The build job builds a local ipfs/kubo:wip image with BuildKit and runs a basic version command.


## State and Persistence Behavior
State is workflow check status and BuildKit/GHA cache entries; no image is pushed.


## Dependencies and Integration Points
Depends on Docker, setup-buildx, hadolint action, docker/build-push-action@v7, go.mod, Dockerfile ARG format, and repository guard conditions.


## Risks and Test Signals
Risks include cache flakiness and Docker daemon availability. Signals catch Dockerfile/toolchain drift and basic image breakage early.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/docker-check.yml -->
