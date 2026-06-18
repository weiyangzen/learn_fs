<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/patches/node-affinity.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/patches/node-affinity.yaml

## Purpose
This default overlay patch applies a preferred scheduling policy for the controller service and provides a commented template for node-service affinity.

## Important Objects and Fields
It patches `StatefulSet/csi-beegfs-controller` with preferred node affinity for nodes carrying `node-role.kubernetes.io/master`, weighted 50. It also includes commented examples for required node affinity on the controller and DaemonSet.

## Control Flow
The default overlay applies this patch by default. Kubernetes scheduling considers it as a soft preference for controller pod placement.

## State and Persistence
Applied affinity persists in the StatefulSet pod template and affects future scheduling decisions.

## Dependencies and Integration Points
It depends on the controller StatefulSet name and cluster node labels. It is part of the production-default overlay and mirrors the dev overlay.

## Risks
The `master` role label is not universal on modern clusters; many use `node-role.kubernetes.io/control-plane`. Because this is only a preference, it will not block scheduling if labels do not match. Users editing commented hard-affinity examples can accidentally prevent scheduling.

## Test Signals
Signals include rendered affinity inspection, scheduler placement behavior on clusters with relevant labels, and successful controller rollout.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/patches/node-affinity.yaml -->
