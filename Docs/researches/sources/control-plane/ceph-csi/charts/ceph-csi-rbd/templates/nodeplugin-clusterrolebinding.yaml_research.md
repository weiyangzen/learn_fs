# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/nodeplugin-clusterrolebinding.yaml

Purpose: binds the RBD nodeplugin ClusterRole to its service account.

Important APIs/types/functions: gated by `.Values.rbac.create`; subject name uses `ceph-csi-rbd.serviceAccountName.nodeplugin`; namespace is `.Release.Namespace`; role name uses the nodeplugin fullname helper.

Control flow: Kubernetes authorization uses this binding when nodeplugin pods call API operations granted by the ClusterRole.

State and persistence behavior: cluster-scoped RBAC binding state.

Dependencies and integration points: depends on service account creation or a preexisting service account with the same resolved name.

Risks: namespace/name mismatches silently leave nodeplugin pods unauthorized. If the service account is reused, it inherits broad nodeplugin privileges.

Test signals: authorization failures in nodeplugin logs and e2e mount/encryption workflows.
