# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/hostpath/csi-hostpath-plugin.yaml

## Purpose
This manifest deploys the distributed hostpath CSI plugin as a DaemonSet. Each node runs a local hostpath driver, node-driver-registrar, liveness probe, and external-provisioner configured for node-local provisioning and capacity tracking.

## Important APIs, Types, And Functions
The main resource is `apps/v1` `DaemonSet` `csi-hostpathplugin`. Containers include `csi-provisioner:v6.3.0` with `--enable-capacity`, `--node-deployment=true`, `--strict-topology=true`, `--immediate-topology=false`, and owner reference args; `csi-node-driver-registrar:v2.17.0`; `hostpathplugin:v1.17.1` with `--capacity=slow=10Gi` and `--capacity=fast=100Gi`; and `livenessprobe:v2.19.0`.

## Control Flow
One pod runs per node. The hostpath driver exposes `/csi/csi.sock`; the registrar registers it with kubelet; the node-local provisioner watches PVCs and publishes CSIStorageCapacity for the pod/node; provisioning is topology-strict so volumes land on the same node as consumers. The deploy script strips capacity settings when the cluster cannot support them.

## State, Persistence, And Dependencies
Each node stores volume data under `/var/lib/csi-hostpath-data/` and socket/registration data under kubelet plugin directories. The driver uses the configured capacity kinds to simulate `fast` and `slow` pools. It depends on privileged hostPath mounts, mount propagation, `/dev`, and downward API node/pod/namespace values.

## Integration Points
It works with `csi-hostpath-fast` and `csi-hostpath-slow` StorageClasses, the distributed CSIDriver, generic ephemeral example, and Prow topology/capacity configuration. The hostpath Go code enforces `kind` capacity parameters based on these StorageClass values.

## Risks
Every pod is privileged and mounts sensitive host directories. Capacity accounting is local to the driver's persisted JSON and simulated with configured sizes; it is not real disk quota. If capacity API lines are removed incorrectly, provisioner and CSIDriver may disagree. Node-local state means volumes are not portable across nodes.

## Test Signals
DaemonSet readiness should equal desired node count. PVCs using fast/slow classes should bind after pod scheduling, capacity objects should appear when supported, and driver `GetCapacity` should reflect per-kind usage after volume creation/deletion.
