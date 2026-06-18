<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/minikube_deploy_all_examples.sh -->
# sources/control-plane/beegfs-csi-driver/operator/hack/minikube_deploy_all_examples.sh

## Purpose
Development helper to deploy a BeeGFS test file system and all Kubernetes examples into Minikube.

## Important APIs, Types, And Functions
Sets `BEEGFS_VERSION=7.4.6` and `BEEGFS_SECRET=mysecret`, applies a test BeeGFS FS manifest with envsubst, waits for pod `beegfs-fs-1-0`, exposes service with `minikube service`, rewrites `/etc/beegfs` config, creates static provisioning directories via `beegfs-ctl`, substitutes management IP into examples, and applies examples.

## Control Flow
Script exits on errors, polls pod status up to 36 times, prints debug information on timeout, then mutates host/minikube BeeGFS config and applies examples.

## State And Persistence
Creates cluster resources, modifies host `/etc/beegfs/connAuth` and `beegfs-client.conf`, creates BeeGFS directories, and edits files under `../examples/k8s/all` in place.

## Dependencies And Integration Points
Requires kubectl, envsubst, minikube, docker, sudo, BeeGFS client utilities, mounted `/etc/beegfs`, and test/example manifests.

## Risks And Edge Cases
Marked non-idempotent. It mutates local example YAMLs and system BeeGFS config. `sudo echo` is ineffective for privilege by itself, but piping through sudo tee writes the connAuth file.

## Test Signals
Manual/minikube smoke path only; no automated test.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/hack/minikube_deploy_all_examples.sh -->
