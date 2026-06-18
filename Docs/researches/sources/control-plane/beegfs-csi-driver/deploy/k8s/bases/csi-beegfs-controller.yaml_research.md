<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-controller.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-controller.yaml

## Purpose
This base manifest defines the controller-service `StatefulSet` for the BeeGFS CSI driver deployment.

## Important Objects and Fields
The `StatefulSet` is named `csi-beegfs-controller`, has one replica, uses service account `csi-beegfs-controller-sa`, runs on host networking, tolerates master scheduling, and contains `csi-provisioner`, `csi-resizer`, and `beegfs` containers. The driver args specify driver name, node ID from `spec.nodeName`, CSI socket endpoint, controller data directory, config/connauth/TLS file paths, node-unstage timeout, and log level.

## Control Flow
At runtime sidecars connect to `/csi/csi.sock` exposed by the privileged `beegfs` container. The controller container mounts config and secret projections, `/host` read-only with bidirectional propagation for wrapped commands, and the plugin directory with host-to-container propagation for mountpoint inspection.

## State and Persistence
Persistent host state is under `/var/lib/kubelet/plugins/beegfs.csi.netapp.com`, shared with node service semantics. The StatefulSet uses `emptyDir` for the controller socket directory and generated ConfigMap/Secret volumes for configuration.

## Dependencies and Integration Points
It integrates the driver image, Kubernetes CSI provisioner and resizer sidecars, generated ConfigMap/Secret names, `chwrap` host execution through `/host`, RBAC service accounts, and operator code that expects stable container names and volume resource names.

## Risks
Privileged host-networked containers with host root mounted are high-trust. The `/host` mount is read-only but bidirectional mount propagation is still powerful. Sidecars are privileged for SELinux socket access. Config and secret names are intended for Kustomize hashing, so raw base application without generators may fail.

## Test Signals
Signals include `kubectl apply -k` deployment, sidecar connection to CSI socket, volume provisioning/resizing, controller pod scheduling on master-capable nodes, operator `deploy_test.go` container-name checks, and e2e example pod creation.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/bases/csi-beegfs-controller.yaml -->
