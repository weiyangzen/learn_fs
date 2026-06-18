<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/openshift-beegfs-client/beegfs-client-ds.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/openshift-beegfs-client/beegfs-client-ds.yaml

Purpose: experimental OpenShift DaemonSet deployment that runs a BeeGFS client service on nodes and exposes client utilities to the CSI driver.

Important APIs and flow: defines a `ServiceAccount`, Role/RoleBinding for the privileged SCC, and a `DaemonSet` using `image-registry.openshift-image-registry.svc:5000/beegfs-csi/beegfs-client:latest`. The container runs `/sbin/init`, executes `/usr/local/sbin/poststart.sh`, stops BeeGFS services on preStop, exposes host port 8006, and mounts `/var/lib/kubelet/plugins/beegfs.csi.netapp.com/client` into `/plugin/client`.

State and persistence: writes shared client config and binaries into the hostPath for CSI node components. Service processes run in a privileged, host-networked container.

Dependencies and integration points: depends on the BuildConfig image, OpenShift SCCs, systemd-capable image, host networking, and kubelet plugin path conventions.

Risks and test signals: privileged host networking and hostPath writes increase blast radius. Test DaemonSet readiness, postStart output, hostPath contents, and CSI mounts on RHCOS/RHEL nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/openshift-beegfs-client/beegfs-client-ds.yaml -->
