# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-rolebinding.yaml

Purpose: binds the namespace Role to the RBD provisioner service account.

Important APIs/types/functions: gated by `.Values.rbac.create`; subject and role names use RBD helper templates and `.Release.Namespace`.

Control flow: enables namespace-scoped leader election and configmap operations for provisioner sidecars.

State and persistence behavior: namespace-scoped RBAC binding only.

Dependencies and integration points: must align with Role and service account names.

Risks: a disabled or mismatched binding causes leader-election/config authorization failures while cluster RBAC may still appear correct.

Test signals: sidecar startup logs and multi-replica leader election.
