<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/statefulset_resource.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/statefulset_resource.yaml

## Purpose
Resource patch that assigns CPU and memory requests/limits to the controller StatefulSet's `juicefs-plugin` container.

## Important APIs, Types, and Resources
Targets `apps/v1` `StatefulSet` `juicefs-csi-controller`; sets limits `cpu: 1000m`, `memory: 1Gi` and requests `cpu: 100m`, `memory: 512Mi`.

## Control Flow
The base kustomization merges this into the controller pod template, leaving sidecar resources unchanged. New controller pods inherit these constraints.

## State and Persistence
No standalone persistence; rendered values persist in the StatefulSet template and affect scheduling/cgroups for controller replicas.

## Dependencies and Integration Points
Depends on Kustomize merge keys and Kubernetes resource quantity support. Integrates with controller leader election and CSI sidecar socket behavior by shaping available CPU/memory.

## Risks
Too-low memory can destabilize provisioning or webhook flows; too-high requests may block scheduling in small clusters. Container-name drift can make the patch ineffective.

## Test Signals
Render the base overlay, inspect pod template resources, and watch controller OOM/throttle metrics during provisioning and webhook tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/statefulset_resource.yaml -->
