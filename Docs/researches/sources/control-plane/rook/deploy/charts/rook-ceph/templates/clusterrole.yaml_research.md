## sources/control-plane/rook/deploy/charts/rook-ceph/templates/clusterrole.yaml

Purpose: defines cluster-scoped RBAC permissions for the Rook Ceph operator, cluster management, mgr, object bucket provisioning, OSD node access, and COSI object storage provisioning.

Important template behavior: gated by `.Values.rbacEnable`. It creates `rook-ceph-system`, `rook-ceph-cluster-mgmt`, `rook-ceph-global`, `rook-ceph-mgr-cluster`, `rook-ceph-mgr-system`, `rook-ceph-object-bucket`, `rook-ceph-osd`, and `objectstorage-provisioner-role`. Permissions include pod/log/exec access, CSI addon/operator resources, CRD get, core services/endpoints/PV/PVC/events, jobs/cronjobs, broad watch/update/status/finalizers across Rook Ceph CRDs, PDBs/deployments/replicasets, OpenShift machine disruption resources, CSIDrivers, NAD get, OBC/OB resources, and COSI resources.

Control flow: static RBAC manifests under one feature flag.

State and persistence: creates powerful cluster roles that enable operator reconciliation across namespaces and storage APIs.

Dependencies and integration points: Kubernetes RBAC, Rook CRDs, objectbucket.io, COSI, CSI addons, OpenShift APIs, and library labels. Risks: broad permissions are operationally necessary but security-sensitive; new CRDs/subresources must be added consistently; disabling RBAC requires pre-provisioned equivalent roles. Tests should compare rendered RBAC to controller permission needs and run e2e under restricted clusters.
