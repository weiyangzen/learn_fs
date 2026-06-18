
# sources/control-plane/rook/deploy/charts/rook-ceph/templates/rolebinding.yaml

Purpose: renders the namespace-scoped `rook-ceph-system` `RoleBinding` when `.Values.rbacEnable` is true. It connects the operator service account to the namespace Role emitted by `role.yaml`.

Important APIs/types/functions: Kubernetes `rbac.authorization.k8s.io/v1` `RoleBinding`, `roleRef` to `Role/rook-ceph-system`, subject `ServiceAccount/rook-ceph-system`, Helm `.Release.Namespace`, `.Values.rbacEnable`, and `include "library.rook-ceph.labels"`.

Control flow: the binding is emitted only in RBAC-enabled installs. Kubernetes resolves the subject in the release namespace and grants it the permissions defined by the same-named Role. The operator deployment relies on this authorization after startup.

State and persistence: the binding persists as RBAC relationship state and has no data plane persistence. Updating or deleting it changes the effective permissions of already-running operator pods because Kubernetes authorizes each API request dynamically.

Dependencies/integration: depends on `serviceaccount.yaml` for the subject and `role.yaml` for the referenced Role. It complements broader cluster roles from the common manifests or chart templates that authorize CRD and cluster-wide operations.

Risks: namespace mismatch between the release and the service account subject leaves the operator under-authorized. Static object names can collide if multiple releases target one namespace. Disabling RBAC requires the operator identity to be bound elsewhere.

Test signals: `helm template` should show matching namespaces in metadata and subject. Runtime checks should verify the operator service account can create/update/delete configmaps, services, pods, and controller workloads in the release namespace.
