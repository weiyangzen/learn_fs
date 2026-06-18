# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/provisioner-clusterrolebinding.yaml

Purpose: binds the RBD provisioner ClusterRole to the provisioner service account.

Important APIs/types/functions: gated by `.Values.rbac.create`; subject uses `ceph-csi-rbd.serviceAccountName.provisioner` in the release namespace; role name uses the provisioner fullname helper.

Control flow: enables the controller Deployment and CSI sidecars to call cluster-scoped storage APIs.

State and persistence behavior: cluster-scoped RBAC binding only.

Dependencies and integration points: requires matching service account and ClusterRole.

Risks: namespace or helper-name drift results in unauthorized sidecars. Reusing the service account gives it broad storage privileges.

Test signals: Kubernetes authorization errors during provisioner startup and storage workflows.
