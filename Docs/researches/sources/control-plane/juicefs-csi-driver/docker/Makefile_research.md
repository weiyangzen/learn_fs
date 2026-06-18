<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/docker/Makefile -->
# sources/control-plane/juicefs-csi-driver/docker/Makefile

## Purpose
Docker image build Makefile for JuiceFS CSI driver, JuiceFS mount images, and dashboard images.

## Important APIs, Types, and Resources
Defines variables for image names, registry, architecture, versions, JuiceFS CE/EE versions, package URLs, and targets such as `image-nightly`, `image-version`, `image-release-check`, `ce-image`, `ce-image-buildx`, `ee-image`, `ee-image-buildx`, `ee-image-4.0-buildx`, `dashboard-build`, and `dashboard-buildx`.

## Control Flow
Targets invoke Docker or Docker Buildx with build contexts for the project and dashboard UI, pass JuiceFS image/version build args, tag images, push multi-arch outputs, and in release-check mode import images into microk8s. Version discovery uses git, Docker, curl, and JuiceFS CLI commands.

## State and Persistence
State is external: built Docker images, pushed registry tags, temporary tar archives during microk8s import, downloaded `juicefs-ee`, and Docker build cache. The Makefile itself persists no runtime data.

## Dependencies and Integration Points
Depends on Docker/Buildx, git, curl, microk8s for import target, GitHub/juicefs release endpoints, Dockerfiles in the same directory, and project/dashboard UI build contexts.

## Risks
Risks include network-dependent version discovery at parse time, mutable latest URLs/tags, accidental pushes, credentials/registry mismatch, multi-arch builder availability, and local `juicefs-ee` artifact churn.

## Test Signals
Signals are dry-run target review with `make -n`, successful multi-arch builds in CI, registry manifest inspection, smoke testing images in k8s, and release-check import on microk8s.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/docker/Makefile -->
