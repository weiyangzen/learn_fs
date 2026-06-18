# sources/control-plane/ceph-csi/e2e/nvmeof/serviceaccount.yaml

Purpose: defines the service account used by the temporary NVMe-oF gateway Deployment.

Important APIs/types/functions: a single `v1 ServiceAccount` named `ceph-nvmeof-gateway`.

Control flow: `createORDeleteGateway()` applies this YAML in `rookNamespace` before the gateway ConfigMap and Deployment. The Deployment references it through both `serviceAccount` and `serviceAccountName`.

State and persistence: creates a namespaced Kubernetes ServiceAccount for the gateway pod. It is deleted during gateway teardown.

Dependencies and integration points: paired with OpenShift SCC user binding and the gateway Deployment. It controls the identity under which the privileged gateway pod is admitted.

Risks: no RBAC is defined in this file; the pod relies mainly on mounted Rook Secrets and SCC privileges. Name changes must be synchronized with `deployment.yaml` and `scc.yaml`.

Test signals: gateway pod can start with this service account, and OpenShift SCC binding matches `system:serviceaccount:<rookNamespace>:ceph-nvmeof-gateway`.
