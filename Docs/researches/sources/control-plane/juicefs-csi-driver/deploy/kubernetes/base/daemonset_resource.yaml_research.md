<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/daemonset_resource.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/daemonset_resource.yaml

## Purpose
Resource patch that assigns CPU and memory requests/limits to the node DaemonSet's `juicefs-plugin` container.

## Important APIs, Types, and Resources
Targets `apps/v1` `DaemonSet` `juicefs-csi-node` in `kube-system`; sets limits `cpu: 1000m`, `memory: 1Gi` and requests `cpu: 100m`, `memory: 512Mi`.

## Control Flow
The base kustomization applies this patch to the node workload after loading `resources.yaml`, adding scheduling and limit metadata without touching the rest of the DaemonSet spec.

## State and Persistence
No state is stored in the file. Once applied, resource settings are persisted in the DaemonSet pod template and influence scheduler reservations and cgroup limits for new node pods.

## Dependencies and Integration Points
Depends on Kustomize strategic merge by container name and Kubernetes resource quantity parsing. Integrates with node plugin performance and cluster capacity planning.

## Risks
Risks are under-provisioning memory for high-volume mount workloads, over-reserving on small nodes, or patch target drift if the container is renamed.

## Test Signals
Render the base overlay and inspect resource fields; run node publish/unpublish load tests and watch pod OOM/throttling metrics.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/base/daemonset_resource.yaml -->
