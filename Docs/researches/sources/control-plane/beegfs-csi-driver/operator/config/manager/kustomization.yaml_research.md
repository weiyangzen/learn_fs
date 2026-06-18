<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manager/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/manager/kustomization.yaml

## Purpose
Builds the operator manager deployment and generated manager ConfigMap.

## Important APIs, Types, And Functions
Includes `manager.yaml`, disables ConfigMap name suffix hashes, generates `manager-config`, and rewrites image `controller` to `ghcr.io/thinkparq/beegfs-csi-driver-operator:v1.8.0`.

## Control Flow
Kustomize loads the deployment, generates config, and applies image substitution.

## State And Persistence
No local state; rendered Deployment and ConfigMap persist in the cluster.

## Dependencies And Integration Points
Consumed by `config/default`. Image values must align with CSV `containerImage` and bundle metadata.

## Risks And Edge Cases
Image tag drift between this file and OLM CSV can publish inconsistent install paths. Disabling hash suffix makes ConfigMap names stable but requires rollout triggers elsewhere if component config changes.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manager/kustomization.yaml -->
