## sources/control-plane/rook/deploy/charts/rook-ceph/templates/clusterrolebinding.yaml

Purpose: binds cluster-scoped roles from `clusterrole.yaml` to the operator and object storage provisioner service accounts.

Important template behavior: gated by `.Values.rbacEnable`. It creates ClusterRoleBindings for `rook-ceph-system`, `rook-ceph-global`, and `rook-ceph-object-bucket` to service account `rook-ceph-system` in the release namespace, plus `objectstorage-provisioner-role-binding` to service account `objectstorage-provisioner`.

Control flow: static manifests with release namespace substitution.

State and persistence: grants cluster-wide permissions to operator and COSI service accounts.

Dependencies and integration points: depends on service account creation from library templates and roles from `clusterrole.yaml`. Risks: namespace mismatch prevents bindings from granting permissions; disabling RBAC requires equivalent external bindings; objectstorage service account must exist when COSI driver is enabled. Render and e2e tests should validate service account names across values variants.
