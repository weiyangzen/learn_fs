<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/namespace.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/namespace.yaml

## Purpose
This manifest creates the default namespace for production-style BeeGFS CSI deployments.

## Important Objects and Fields
It defines a `v1` `Namespace` named `beegfs-csi`. The comment notes the name is subject to Kustomize namespace transformation.

## Control Flow
The default overlay includes this file as a resource. Applying the overlay creates the namespace before namespaced resources are applied.

## State and Persistence
The namespace persists in the Kubernetes API server and scopes namespaced CSI controller/node support resources such as service accounts, roles, role bindings, ConfigMaps, Secrets, StatefulSet, and DaemonSet.

## Dependencies and Integration Points
It integrates with the default overlay's `namespace: beegfs-csi` setting and all namespaced base resources. Cluster-scoped resources such as CSIDriver and ClusterRole are not scoped by it.

## Risks
Changing the namespace affects where service accounts, pods, and generated config/secrets live. Existing deployments may leave resources in the old namespace if not cleaned up.

## Test Signals
Signals include rendered overlay namespace fields, successful namespace creation, and pods/resources appearing under `beegfs-csi`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/namespace.yaml -->
