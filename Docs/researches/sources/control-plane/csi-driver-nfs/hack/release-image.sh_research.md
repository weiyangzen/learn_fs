<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/release-image.sh -->
# sources/control-plane/csi-driver-nfs/hack/release-image.sh

## Purpose
Publishes CSI NFS container images to an Azure Container Registry-backed release flow and checks the public latest image after a delay.

## Important APIs, Types, and Functions
The script expects one argument, an ACR registry name. It exports `OUTPUT_TYPE=registry`, `REGISTRY_NAME`, `REGISTRY=${REGISTRY_NAME}.azurecr.io`, `IMAGENAME=public/k8s/csi/nfs-csi`, `CI=1`, and `PUBLISH=1`, then runs `az acr login`, `make`, `make container push push-latest`, `docker pull`, and `docker inspect`.

## Control Flow, State, and Persistence
With `set -euo pipefail`, any failing command exits. After publishing it sleeps for 60 seconds, pulls `mcr.microsoft.com/k8s/csi/nfs-csi:latest`, and prints the image creation timestamp from `docker inspect`. Persistent effects are registry writes and local Docker image/cache changes.

## Dependencies and Integration Points
It depends on Azure CLI authentication, Docker, Makefile release targets, Azure Container Registry, and Microsoft Container Registry propagation. It is part of manual or CI release operations rather than normal build verification.

## Risks and Test Signals
Risks include publishing to the wrong registry, credentials leakage through shell environment, unquoted registry variables, propagation delays longer than 60 seconds, and use of mutable `latest`. Signals are successful ACR login, successful make/push targets, a pullable MCR image, and an updated `Created` timestamp.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/release-image.sh -->
