# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/hostpath/csi-hostpath-plugin.yaml

## Purpose
This manifest deploys the all-in-one Kubernetes 1.30 hostpath CSI plugin. Unlike the split test deployment, it bundles controller sidecars, registrar, liveness probe, RBAC bindings, and the driver into one StatefulSet and service account.

## Important APIs, Types, And Functions
It creates `ServiceAccount` `csi-hostpathplugin-sa`, ClusterRoleBindings/RoleBindings to external sidecar roles, and a one-replica `StatefulSet` `csi-hostpathplugin`. Containers include `hostpathplugin:v1.17.0`, health monitor controller `v0.16.0`, node-driver-registrar `v2.15.0`, livenessprobe `v2.17.0`, attacher `v4.10.0`, provisioner `v6.0.0`, resizer `v2.0.0`, and snapshotter `v8.4.0`.

## Control Flow
The deploy script first applies upstream RBAC, then this manifest binds those roles to the plugin service account. The StatefulSet starts one pod on a single node; the driver creates `/csi/csi.sock`; every sidecar in the pod connects locally to that socket; the registrar exposes its own HTTP health endpoint; liveness probe monitors the driver health port.

## State, Persistence, And Dependencies
Persistent test data lives in `/var/lib/csi-hostpath-data/`. Kubelet socket, plugin registry, pod mount paths, plugin directories, and `/dev` are mounted from the host. Marker comments allow deploy-time insertion of snapshot metadata sidecar, volumes, and hostpath args. The manifest depends on privileged pods and compatible RBAC resources named by external sidecar deployments.

## Integration Points
This is the primary Kubernetes 1.30 deployment target for storage e2e tests. It integrates with snapshot class, CSIDriver, testing socat, deploy-script image substitution, optional snapshot metadata, optional volume mode conversion, and Prow test driver generation.

## Risks
The pod has broad privileged host access and should remain a test driver. All sidecars share one pod lifecycle, so a single crash can affect the whole stack. Role binding names must match upstream RBAC resource names. The leading indentation before the opening comment is harmless YAML-wise only because comments are ignored, but it is visually odd. Data survives pod and resource deletion unless node directories are cleaned.

## Test Signals
`kubectl describe statefulset csi-hostpathplugin` should show one ready replica. Sidecar logs should show successful leader election/CSI socket connection. Kubelet plugin registration, PVC provisioning, attachment, resizing, snapshots, and health monitor tests should all use this single pod.
