## sources/control-plane/csi-driver-iscsi/deploy/uninstall-driver.sh

Purpose: removes csi-driver-iscsi manifests from a cluster.

Control flow mirrors install: choose master or specified version, optionally use local deploy files, append version subdirectory for non-master, then `kubectl delete -f` driverinfo and node manifests. State changes are deletion of Kubernetes resources.

Dependencies are bash, kubectl, manifest availability, and cluster access. Risks include unquoted version test, failures if resources already absent, and leaving host-side iSCSI sessions, mountpoints, sockets, or connector JSON if workloads are still using volumes. Test signal is kubectl delete status.
