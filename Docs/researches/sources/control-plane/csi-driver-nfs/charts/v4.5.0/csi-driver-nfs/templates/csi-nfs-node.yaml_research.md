# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-nfs-node.yaml

## Purpose

This template deploys the v4.5.0 NFS CSI node `DaemonSet`, running the liveness probe, node-driver-registrar, and privileged NFS plugin on every selected Linux node.

## APIs, control flow, and state

The DaemonSet renders rolling update settings, host networking, DNS policy, image pull secrets, priority, node selectors, tolerations, resources, and images from values. v4.5.0 changes the service account from a hard-coded `csi-nfs-node-sa` to `.Values.serviceAccount.node`, making custom service-account names viable. The registrar registers `${kubeletDir}/plugins/csi-nfsplugin/csi.sock` with kubelet. The NFS plugin runs with `SYS_ADMIN`, receives node identity and CSI endpoint, mounts the socket directory and `${kubeletDir}/pods`, and optionally mounts host `/etc/nfsmount.conf` and `/etc/nfsmount.conf.d` when `.Values.feature.propagateHostMountOptions` is true.

## Dependencies and integration points

The template integrates with kubelet plugin registration, host mount propagation, host NFS configuration, Linux nodes, the `CSIDriver` object, and the node service account. State lives in host plugin sockets, kubelet registration paths, and active mounts rather than in chart-managed storage.

## Risks and test signals

The optional host NFS config propagation increases host coupling and can expose node-specific mount behavior to the plugin. The privileged container remains high risk. Test DaemonSet rollout, plugin registration, custom `.Values.serviceAccount.node`, both values of `propagateHostMountOptions`, custom kubelet directories, pod volume mounts, liveness probes, and node drain/rolling update behavior.
