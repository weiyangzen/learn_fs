<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/minikube_install_driver_prerequisites.sh -->
# sources/control-plane/beegfs-csi-driver/operator/hack/minikube_install_driver_prerequisites.sh

## Purpose
Installs BeeGFS user-space prerequisites into a Minikube node for development testing.

## Important APIs, Types, And Functions
Runs `minikube ssh` commands to reset apt source list snippets, install wget, add BeeGFS 7.4.6 GPG key and focal repository, install `beegfs-utils`, and download a default `beegfs-client.conf`.

## Control Flow
Sequential shell script with `set -euo pipefail`; any failed SSH/package command aborts.

## State And Persistence
Mutates package sources and `/etc/beegfs/beegfs-client.conf` inside the Minikube environment.

## Dependencies And Integration Points
Depends on apt-based Minikube image, network access to beegfs.io and GitHub, and the companion deploy script.

## Risks And Edge Cases
Deletes all `/etc/apt/sources.list.d/*` entries in Minikube, which may remove unrelated repos. Pins BeeGFS focal repo regardless of host/minikube distro.

## Test Signals
Manual setup helper only.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/minikube_install_driver_prerequisites.sh -->
