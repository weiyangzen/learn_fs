# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose

This template deploys the node half of the NFS CSI driver as an `apps/v1` `DaemonSet`. Each Linux node runs a liveness probe, the CSI node-driver-registrar, and the privileged NFS plugin so kubelet can discover the driver and publish NFS volumes into pods.

## APIs, control flow, and state

The DaemonSet uses a rolling update strategy with `.Values.node.maxUnavailable`, host networking, configurable DNS policy, node selectors, tolerations, priority, and resource requests. The registrar exposes kubelet registration through `${kubeletDir}/plugins_registry` and points kubelet at `${kubeletDir}/plugins/csi-nfsplugin/csi.sock`. The NFS container receives node identity from `spec.nodeName`, exposes the CSI endpoint on the hostPath socket directory, and runs with `SYS_ADMIN`, privilege, and bidirectional propagation on `${kubeletDir}/pods`.

Node-side state is mostly socket and mount state in hostPath directories. The socket directory is `DirectoryOrCreate`; pod mount state lives under kubelet's pod directory; registration uses kubelet's plugin registry directory. The DaemonSet does not persist application data itself.

## Dependencies and integration points

The node pods integrate directly with kubelet CSI plugin registration, Linux mount namespaces, NFS client tooling inside the plugin image, host networking, and the `CSIDriver` object. In v4.4.0 the service account name is hard-coded as `csi-nfs-node-sa`, which must line up with RBAC/service-account creation.

## Risks and test signals

The privileged container and bidirectional host mounts create a high-impact security surface. The hard-coded node service account makes custom service-account naming brittle in this version. The template also lacks the later optional propagation of host `/etc/nfsmount.conf`, so node-level NFS mount tuning may not reach the plugin. Test by checking DaemonSet rollout on Linux nodes, kubelet plugin registration, `kubectl describe csinode`, successful pod volume mounts, liveness behavior on the node health port, and custom `kubeletDir` rendering.
