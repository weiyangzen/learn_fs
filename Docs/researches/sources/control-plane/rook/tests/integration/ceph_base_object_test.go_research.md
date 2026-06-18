# sources/control-plane/rook/tests/integration/ceph_base_object_test.go

Shared RGW/CephObjectStore helper layer. It creates/deletes object stores, validates RGW deployment/service/status readiness, creates/checks object-store users, and generates test TLS secrets.

Key functions are `runObjectE2ETestLite`, `RgwServiceName`, `createCephObjectStore`, `deleteObjectStore`, `assertObjectStoreDeletion`, `createCephObjectUser`, `checkCephObjectUser`, `objectStoreCleanUp`, and `generateRgwTlsCertSecret`. Creation optionally generates TLS, creates a CephObjectStore, waits for RGW pods/deployments, polls object-store status for `Ready` or legacy `Connected`, checks endpoint info, service reachability, and dashboard-admin user presence. Deletion verifies deletion-unblocked conditions before final absence.

State includes CephObjectStore CRs, RGW deployments/services, TLS Secrets, CephObjectStoreUser CRs/secrets, dashboard users, and RGW realm/zone/pool resources. Dependencies are Rook API types, object/user clients, `K8sHelper`, installer command execution, `k8sutil.ReadyStatus`, Kubernetes clients, and `tests/scripts/generate-tls-config.sh`.

Risks: RGW pod prefix checks can be confused by multiple stores; dashboard-admin errors are logged only; deletion assumes status is readable after delete; package globals couple object tests. Signals include object-store phase/endpoint, RGW pod/deployment readiness, service up, deletion condition status/reason, user secret existence, RGW user info, and Kubernetes user phase.
