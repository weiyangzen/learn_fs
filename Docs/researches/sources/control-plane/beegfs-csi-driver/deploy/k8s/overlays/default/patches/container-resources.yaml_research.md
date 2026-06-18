<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/patches/container-resources.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/patches/container-resources.yaml

## Purpose
This optional default overlay patch is a template for adjusting resource requests and limits for BeeGFS CSI workloads.

## Important Objects and Fields
It defines strategic merge patches for `StatefulSet/csi-beegfs-controller` and `DaemonSet/csi-beegfs-node`, setting resource defaults for `beegfs`, `csi-provisioner`, `node-driver-registrar`, and `liveness-probe`.

## Control Flow
The file is not applied unless a user adds it to `patchesStrategicMerge` in the overlay Kustomization. Once enabled, Kustomize merges matching container entries by name into the rendered workloads.

## State and Persistence
Applying the patch changes pod templates in the cluster and can trigger rollout. It owns no state when left unreferenced.

## Dependencies and Integration Points
It depends on stable workload/container names from base manifests. It is intended as a user customization starting point.

## Risks
The DaemonSet section has inconsistent indentation around `metadata`, `template`, and container entries; if enabled, YAML parsing or strategic merge may fail. The liveness-probe request in this patch uses CPU `100m`, while the base manifest uses `60m`, so comments that values are defaults are not fully aligned.

## Test Signals
Signals include enabling the patch, running `kubectl kustomize`, verifying rendered resource fields, and observing scheduling/admission with customized limits.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/patches/container-resources.yaml -->
