<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-rbac.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-rbac.yaml

## Purpose
This base manifest defines service accounts and RBAC needed by the BeeGFS CSI controller and node services, including an OpenShift SCC role.

## Important Objects and Fields
It creates `csi-beegfs-controller-sa` and `csi-beegfs-node-sa`. The `csi-beegfs-provisioner-role` ClusterRole grants PV/PVC/storageclass/event/csinode/node/pod access and PVC status patching. `csi-beegfs-provisioner-binding` binds that role to the controller service account. The namespaced `csi-beegfs-privileged-scc-role` allows use of OpenShift `privileged` SCC, and its RoleBinding grants that use to both controller and node service accounts.

## Control Flow
Kubernetes authorizes sidecars and the driver based on these bindings. The provisioner sidecar needs cluster-level storage object access, and OpenShift deployments need SCC use before privileged host-network pods can start.

## State and Persistence
The resources persist in the Kubernetes API server. They do not create local filesystem state.

## Dependencies and Integration Points
`deploy.go` embeds and parses this multi-document YAML with `GetRBAC()`. Kustomize includes it in bases, and operator logic consumes the typed objects returned by the deploy package.

## Risks
RBAC permissions are broad enough for provisioning and eventing and should be reviewed when sidecar versions change. The OpenShift SCC role is harmless on non-OpenShift only if the API server tolerates unknown API groups in RBAC rules, which Kubernetes does. Document splitting in `GetRBAC()` depends on each document containing recognizable `kind` text.

## Test Signals
Signals include strict unmarshal of all RBAC documents, controller provisioning success, OpenShift pod admission, and CI/unit tests that assert only expected RBAC object types are returned.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-rbac.yaml -->
