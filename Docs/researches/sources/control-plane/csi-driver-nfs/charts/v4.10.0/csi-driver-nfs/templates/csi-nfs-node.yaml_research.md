# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: v4.10.0 node DaemonSet with optional host NFS mount option propagation.

Important APIs/types/functions: `DaemonSet`; livenessprobe, node-driver-registrar, NFS containers; values for serviceAccount.node, image baseRepo composition, dnsPolicy, resources, kubeletDir, and `.Values.feature.propagateHostMountOptions`.

Control flow: Host-networked Linux pods register the CSI socket, run liveness checks, and serve node CSI. When host mount option propagation is enabled, `/etc/nfsmount.conf` and `/etc/nfsmount.conf.d` are mounted into the NFS container.

State and persistence: Node socket/registration/pod mount state plus optional host NFS configuration mounts.

Dependencies and integration points: Kubelet, node service account, CSIDriver, and host NFS client config.

Risks: Mounting host NFS config can couple pod behavior to node drift. Privileged NFS container remains high risk. Test signals: node rollout, registration, and mount option propagation test.
