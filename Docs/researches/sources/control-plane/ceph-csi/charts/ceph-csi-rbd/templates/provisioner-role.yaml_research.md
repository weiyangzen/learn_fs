# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-role.yaml

Purpose: renders namespace-scoped RBAC for provisioner leader election and configmap management.

Important APIs/types/functions: gated by `.Values.rbac.create`; grants configmaps `get/list/watch/create/update/delete` and leases `get/watch/list/delete/update/create`.

Control flow: external CSI sidecars use Leases for leader election and may use ConfigMaps for legacy locks/config.

State and persistence behavior: namespace-scoped RBAC; authorized controllers persist Lease/ConfigMap objects.

Dependencies and integration points: bound by the RoleBinding to the provisioner service account.

Risks: configmap delete/update permissions are broad in the namespace. Namespace mismatch breaks leader election.

Test signals: sidecar leader-election logs and HA provisioner e2e behavior.
