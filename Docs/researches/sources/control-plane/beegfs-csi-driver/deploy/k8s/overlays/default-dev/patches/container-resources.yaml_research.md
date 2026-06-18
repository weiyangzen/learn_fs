<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/container-resources.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/container-resources.yaml

## Purpose
This optional development patch is a template for adjusting resource requests and limits on controller and node deployment containers.

## Important Objects and Fields
It contains strategic merge fragments for `StatefulSet/csi-beegfs-controller` and `DaemonSet/csi-beegfs-node`, setting memory limits and CPU/memory requests for `beegfs`, `csi-provisioner`, `node-driver-registrar`, and `liveness-probe`.

## Control Flow
The file is not referenced by default. If uncommented in the overlay Kustomization, Kustomize strategic merge patches matching containers by name and replaces their `resources` fields.

## State and Persistence
No runtime state is created by the file alone. Applying it changes pod specs in the cluster, which can trigger rollouts.

## Dependencies and Integration Points
It depends on stable workload and container names from base manifests. It is a developer customization point and mirrors the production overlay template.

## Risks
The DaemonSet YAML indentation appears inconsistent around the container list, which may make the patch invalid if enabled. Resource values are examples/defaults and may be unsuitable for real workloads. Container name drift will cause patches not to apply.

## Test Signals
Signals include enabling the patch and running `kubectl kustomize`, validating YAML parse success, inspecting rendered resource fields, and observing pod scheduling/admission.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/container-resources.yaml -->
