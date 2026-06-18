# sources/control-plane/csi-driver-smb/hack/release-image.sh

## Purpose
Release helper to build and publish Linux/Windows SMB CSI images to Azure Container Registry and inspect the public latest image.

## Important APIs, Types, and Functions
Shell script requiring registry name argument. Exports `REGISTRY_NAME`, `REGISTRY`, `IMAGENAME`, `CI`, `PUBLISH`, and `WINDOWS_USE_HOST_PROCESS_CONTAINERS`, runs `az acr login`, then make targets.

## Control Flow
Validates an argument, logs into ACR, runs `make container-all container-windows-hostprocess-latest push-manifest push-latest`, waits 60 seconds, pulls `mcr.microsoft.com/k8s/csi/smb-csi:latest`, and prints image creation metadata.

## State and Persistence
Mutates local Docker image cache, ACR registry content, public manifest/tag state, and environment for make.

## Dependencies
Requires bash, Azure CLI, Docker, Makefile targets, registry credentials, and network access.

## Integration Points
Part of release automation for publishing multi-platform images referenced by manifests and Helm chart.

## Risks and Edge Cases
Publishes mutable `latest`; unquoted registry variable usage is fragile; release success depends on delayed external registry propagation.

## Test Signals
Successful ACR login, make completion, docker pull success, and `docker inspect` Created output.
