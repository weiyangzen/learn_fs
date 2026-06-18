# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose

This v4.6.0 template deploys the node `DaemonSet` for the NFS CSI driver. It provides kubelet CSI registration, liveness probing, and privileged node-side NFS mount handling.

## APIs, control flow, and state

The DaemonSet renders host networking, DNS policy, image pull secrets, priority, scheduling constraints, tolerations, rolling update settings, resources, and images from values. Like the controller, v4.6.0 adds slash-prefixed repository support with `.Values.image.baseRepo`. It switches liveness-probe arguments to `--http-endpoint=localhost:<port>`, removes explicit healthz container ports, and makes Kubernetes liveness checks use numeric ports on localhost.

The registrar registers the CSI socket under `${kubeletDir}/plugins/csi-nfsplugin/csi.sock`. The NFS plugin remains privileged with `SYS_ADMIN` and bidirectional mount propagation to `${kubeletDir}/pods`; sidecars and plugin now drop all capabilities except the explicit add. Optional host NFS config propagation mounts `/etc/nfsmount.conf` and `/etc/nfsmount.conf.d`.

## Dependencies and integration points

This template integrates with kubelet plugin registration, Linux host paths, mount namespaces, the `CSIDriver` object, NFS client behavior, image registries, and node scheduling. Runtime state is sockets, registration files, and mounts on the host.

## Risks and test signals

Image mirror composition can fail if repository values are malformed. Capability dropping and health endpoint changes need runtime validation. Host NFS config propagation may differ across distributions. Test default and mirrored images, DaemonSet rollout, kubelet registration, `CSINode` updates, pod volume mounts, liveness probes, custom `kubeletDir`, and both settings of `propagateHostMountOptions`.
