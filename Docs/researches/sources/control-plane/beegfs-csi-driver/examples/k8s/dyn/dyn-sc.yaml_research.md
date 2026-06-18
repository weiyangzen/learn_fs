<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-sc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-sc.yaml

Purpose: standalone dynamic BeeGFS StorageClass.

Important APIs and flow: declares BeeGFS CSI provisioner with `sysMgmtdHost`, `volDirBasePath`, optional stripe/permission keys, `Delete` reclaim policy, immediate binding, and volume expansion enabled.

State and persistence: controls dynamic directory lifecycle and expansion requests for PVCs using the class.

Dependencies and integration points: integrates with Kubernetes storage APIs, BeeGFS management daemon, and driver parameter parsing.

Risks and test signals: all StorageClass parameters are strings; unquoted numeric optional values can be rejected or misparsed. Test provision/delete/expand flows and controller logs.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/dyn/dyn-sc.yaml -->
