# sources/control-plane/csi-driver-nfs/charts/v4.13.1/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose
This template renders the node-plugin `DaemonSet` that registers the NFS CSI driver with kubelet and performs node-side NFS mount operations on every selected Linux node.

## Important APIs, Types, and Functions
It emits an `apps/v1` `DaemonSet` with `liveness-probe`, `node-driver-registrar`, and privileged `nfs` containers. It uses host paths for the CSI socket directory, kubelet pod mounts, and kubelet plugin registry. Optional host mount option propagation mounts `/etc/nfsmount.conf` and `/etc/nfsmount.conf.d` when `feature.propagateHostMountOptions` is true.

## Control Flow, State, and Persistence
The DaemonSet uses rolling updates, host networking, Linux node selection, tolerations, optional affinity, and bidirectional mount propagation. The registrar publishes `{{ .Values.kubeletDir }}/plugins/csi-nfsplugin/csi.sock` to kubelet. Node state lives in host plugin directories, registration sockets, mounted pod volumes, and NFS mounts rather than in container filesystems.

## Dependencies and Integration Points
It depends on the node service account from RBAC, kubelet directory layout, `CSIDriver` metadata, and kubelet plugin registration behavior. The driver name must match controller, storage classes, and the `CSIDriver`.

## Risks and Test Signals
The v4.13.1 template uses `dnsPolicy: {{ .Values.controller.dnsPolicy }}` instead of `node.dnsPolicy`, so node-specific DNS overrides are ignored. Other risks include privileged `SYS_ADMIN`, host path availability, registration path mismatch on nonstandard kubelet directories, and host mount option propagation exposing host config. Signals are DaemonSet rollout on all intended nodes, registrar health endpoint, `kubectl get csinode` driver entries, pod mount/unmount tests, and DNS tests when overriding node policy.
