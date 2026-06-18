<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/docker-image.yml -->

# sources/distributed-fs/ipfs-kubo/.github/workflows/docker-image.yml


## Purpose
Official Docker image build and publish workflow for Kubo releases/branches/manual dispatch.


## Important APIs, Types, and Functions
Triggers on workflow_dispatch with push/tags inputs and pushes to master/staging/bifrost-* branches or v* tags. Job docker-hub checks out, sets QEMU/Buildx, logs into Docker Hub, computes tags, reads Go version, builds amd64/armv7/arm64 images separately, smoke-tests them, then conditionally publishes multi-arch images and cache.


## Control Flow
The workflow builds each architecture with GO_VERSION from go.mod, uses registry/GHA cache, tests images with timeout/retry under QEMU where needed, and only pushes on non-manual or manual push=true.


## State and Persistence Behavior
State is Docker Hub images/tags, build cache, and workflow outputs. Secrets/vars provide Docker credentials.


## Dependencies and Integration Points
Depends on Docker Hub credentials, bin/get-docker-tags.sh, Dockerfile, docker/build-push-action@v7, QEMU emulation, Buildx, and GitHub event inputs.


## Risks and Test Signals
Risks include credential exposure scope, QEMU flakiness, tag-generation mistakes, and publish conditions. Signals validate all release image platforms before publication.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/docker-image.yml -->
