<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/kustomization.yaml

## Purpose
This Kustomize base lists the core BeeGFS CSI deployment resources.

## Important Objects and Fields
The Kustomization uses `apiVersion: kustomize.config.k8s.io/v1beta1` and includes controller StatefulSet, RBAC, CSIDriver, and node DaemonSet resources.

## Control Flow
Kustomize consumers include this base directly or through version/overlay layers. It provides no transformations itself.

## State and Persistence
No runtime state is owned by this file. Applying the rendered Kustomize output creates the listed Kubernetes objects.

## Dependencies and Integration Points
It integrates the base manifests for user overlays and version-specific overlays referenced by default overlays. Any added base resource should be considered for `deploy.go` embedding if the operator also needs it.

## Risks
Missing resources here will be absent from Kustomize deployments even if embedded in operator code. Conversely, resources added here but not embedded may diverge operator and direct deployment behavior.

## Test Signals
Signals include `kubectl kustomize` or `kubectl apply -k` on overlays, direct base rendering, and comparison with operator embedded resources.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/kustomization.yaml -->
