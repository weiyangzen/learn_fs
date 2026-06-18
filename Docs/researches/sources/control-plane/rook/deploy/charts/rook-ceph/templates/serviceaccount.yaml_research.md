
# sources/control-plane/rook/deploy/charts/rook-ceph/templates/serviceaccount.yaml

Purpose: creates the service accounts used by the Rook Ceph operator and by the Ceph COSI driver.

Important APIs/types/functions: Kubernetes `v1` `ServiceAccount`, Helm `.Release.Namespace`, `include "library.rook-ceph.labels"`, and `include "library.imagePullSecrets"`. It emits `rook-ceph-system` with chart labels and `objectstorage-provisioner` with COSI driver labels.

Control flow: both service accounts are rendered unconditionally by this template. Any configured image pull secrets are inserted into both accounts through the shared library helper. Other RBAC templates bind these identities to namespace and cluster permissions.

State and persistence: service accounts are persistent Kubernetes identities. They produce tokens/credentials through Kubernetes mechanisms and become the subject used by operator and COSI workloads.

Dependencies/integration: `rook-ceph-system` integrates with operator deployments and RBAC in `role.yaml`, `rolebinding.yaml`, and broader common roles. `objectstorage-provisioner` integrates with COSI `Bucket*` resources and the object storage provisioner ClusterRole/ClusterRoleBinding.

Risks: adding pull secrets to both identities can widen registry credential availability. If RBAC is disabled or bindings are absent, service accounts exist but workloads fail authorization. The COSI account is useful only when COSI CRDs/controllers are installed.

Test signals: render with and without image pull secrets; verify service account names and namespaces match all RoleBinding and ClusterRoleBinding subjects; run operator and COSI pod startup smoke tests.
