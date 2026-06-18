<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/node-affinity.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/node-affinity.yaml

## Purpose
This development patch sets preferred scheduling for the controller service and provides a commented template for node-service affinity.

## Important Objects and Fields
It patches `StatefulSet/csi-beegfs-controller` with `preferredDuringSchedulingIgnoredDuringExecution` node affinity that prefers nodes with `node-role.kubernetes.io/master` at weight 50. A commented DaemonSet block shows how to add required node affinity.

## Control Flow
The default-dev Kustomization applies this patch. Kubernetes scheduling uses it as a preference, not a hard requirement, for controller pods.

## State and Persistence
Applying the overlay persists affinity in the StatefulSet pod template. It can influence future pod scheduling and rollouts.

## Dependencies and Integration Points
It depends on the controller StatefulSet name and Kubernetes node labels. It mirrors the production default overlay patch.

## Risks
Many clusters now use `node-role.kubernetes.io/control-plane` instead of `master`; the preference may be ineffective. Users may misunderstand the commented DaemonSet block as active policy. Hard affinity additions can prevent DaemonSet scheduling if labels are wrong.

## Test Signals
Signals include rendered pod spec inspection, scheduler placement on labeled nodes, and deployment behavior on clusters with `master`, `control-plane`, or neither label.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/node-affinity.yaml -->
