# sources/control-plane/csi-driver-smb/charts/v1.2.0/csi-driver-smb/templates/csi-smb-node.yaml

## Purpose
This template renders the Linux SMB CSI node `DaemonSet` for chart `v1.2.0` when `.Values.linux.enabled` is true. It installs the node plugin on every selected Linux node so kubelet can register `smb.csi.k8s.io` and mount SMB-backed volumes.

## Important APIs, Types, And Functions
The Kubernetes API is `apps/v1/DaemonSet`. Containers include `liveness-probe`, `node-driver-registrar`, and `smb`. The registrar points kubelet at `.Values.linux.kubelet/plugins/.Values.driver.name/csi.sock`; the SMB plugin receives `CSI_ENDPOINT`, `KUBE_NODE_NAME`, driver name, log level, and feature flags such as `--enable-get-volume-stats` in later versions. Resource values come from `.Values.node.resources`.

## Control Flow
Helm gates the whole file on `.Values.linux.enabled`, sets rolling update `maxUnavailable` in versions that support it, injects labels/annotations/pull secrets, selects `kubernetes.io/os: linux`, and applies tolerations plus node selector overrides. The pod uses host networking and the configured Linux DNS policy in newer versions.

## State And Persistence Behavior
The DaemonSet persists socket and registration paths through hostPath volumes under the kubelet directory and mounts the kubelet tree with bidirectional mount propagation. The SMB container is privileged so node-stage and publish operations can affect host mounts.

## Dependencies And Integration Points
It depends on kubelet plugin registration, Linux CIFS/SMB mount support in the node image/host, the node service account in modern versions, liveness-probe and registrar images, and the `CSIDriver` name matching exactly.

## Risks And Test Signals
Risks include hostPath mistakes, privileged mount propagation failures, OS selector drift, invalid image composition, and stale registration sockets. Test with `helm template`, DaemonSet rollout, `kubectl get csinode`, kubelet plugin registration events, PVC mount/unmount, and volume stats when enabled. One template risk in these early versions is that `.Values.node.affinity` appears under the `nodeSelector` block rather than as a sibling `affinity` field.
