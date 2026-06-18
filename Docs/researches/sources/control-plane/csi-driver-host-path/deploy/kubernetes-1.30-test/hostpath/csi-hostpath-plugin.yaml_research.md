# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-plugin.yaml

## Purpose
This manifest deploys the core hostpath CSI plugin for the split Kubernetes 1.30 test setup. It runs the driver, liveness probe, external health monitor controller, and node-driver-registrar in a single one-replica StatefulSet pinned to one node.

## Important APIs, Types, And Functions
The resource is a `StatefulSet` named `csi-hostpathplugin`. The `hostpath` container runs `hostpathplugin:v1.15.0` with `--drivername=hostpath.csi.k8s.io`, `--endpoint=$(CSI_ENDPOINT)`, and `--nodeid=$(KUBE_NODE_NAME)`. Sidecars include `livenessprobe:v2.15.0`, `csi-external-health-monitor-controller:v0.14.0`, and `csi-node-driver-registrar:v2.13.0`. It exposes health port `9898` and registrar socket registration path `/var/lib/kubelet/plugins/csi-hostpath/csi.sock`.

## Control Flow
Kubernetes starts one privileged driver pod. The driver creates `/csi/csi.sock`; the registrar registers that socket with kubelet; liveness probes call CSI health through the socket; health-monitor-controller talks to the controller service. Other split sidecars use pod affinity and the shared hostPath socket directory.

## State, Persistence, And Dependencies
Driver data persists under hostPath `/var/lib/csi-hostpath-data/` mounted at `/csi-data-dir`. The driver also mounts kubelet pods and plugin directories with bidirectional propagation plus `/dev` for block volume loop devices. It depends on privileged pod admission, kubelet plugin registry presence, and the node name downward API.

## Integration Points
The manifest is rendered by the deploy script for image/path overrides and optional snapshot metadata insertion. It is the socket endpoint for attacher, provisioner, resizer, snapshotter, health monitor, socat testing, and kubelet registration.

## Risks
This is a privileged test driver with broad hostPath access. Single-replica topology means volumes only work on one node; the deploy script appends a Prow client node to avoid late-binding placement errors. Version skew with split sidecars can surface as CSI RPC or RBAC failures. Host data under `/var/lib/csi-hostpath-data` survives pod recreation and destroy.

## Test Signals
Readiness should show the StatefulSet ready and HTTP liveness passing. Kubelet should list the driver from the registrar, dynamic provisioning should create data directories, node publish should bind mount under kubelet pod paths, and block tests should create loop devices via `/dev` access.
