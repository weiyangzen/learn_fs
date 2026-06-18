# sources/cloud-native/containerd/.github/workflows/build-test-images.yml

## Purpose
This manual workflow builds and pushes Windows-backed volume test images to a target registry namespace.

## Important APIs, Types, And Functions
It accepts workflow-dispatch inputs for target project, Azure Windows image, VM size, and Azure location. It uses Azure login/CLI, Docker installation, SSH key generation, Windows helper scripts, GHCR login, and Makefile targets under `integration/images/volume-copy-up` and `volume-ownership`.

## Control Flow
The job checks out containerd, installs Go and Docker, creates an Azure resource group and Windows helper VM, prepares Windows Docker and SSH/TLS access, fetches Docker client certificates, logs in to GHCR, builds/pushes multi-platform test images through a remote Windows Docker endpoint, and always deletes the Azure resource group.

## State And Persistence
Persistent outputs are pushed container images. Transient state includes Azure resource groups/VMs, SSH keys, Docker TLS certs, and local buildx state.

## Dependencies And Integration Points
It depends on `AZURE_SUB_ID`, `AZURE_CREDS`, GHCR package permissions, repository Windows setup scripts, Docker packages, and integration image Makefiles.

## Risks
The workflow opens SSH and Docker TLS ports on a public VM and relies on cleanup in an `always()` step. Azure quota, image availability, and remote Docker readiness can fail independently of repository code. The generated password is masked, but VM provisioning still uses password auth initially.

## Test Signals
Manual run success, image availability in GHCR, and subsequent Windows integration tests pulling those images are the main signals.
