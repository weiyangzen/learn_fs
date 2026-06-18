# sources/control-plane/rook/tests/framework/clients/object.go

Purpose: `ObjectOperation` manages Rook `CephObjectStore` resources for RGW/S3/Swift integration tests and exposes endpoint discovery.

Important APIs/types/functions: package logger and constant `rgwPort = 80`; constructor `CreateObjectOperation`; methods `Create`, `Delete`, and `GetEndPointUrl`.

Control flow: `Create` applies a rendered object store manifest, waits up to 80 retries for RGW pods matching `rook_object_store=<storeName>`, then creates an external NodePort RGW service. `Delete` deletes the `CephObjectStore` resource and waits for pods with the store label to disappear. `GetEndPointUrl` queries the service cluster IP with label `rgw=<storeName>` and appends port 80.

State and persistence behavior: persistent external state includes object store CRs, RGW deployments/pods/services, and Ceph object pools/users managed by the operator.

Dependencies and integration points: depends on `CephManifests.GetObjectStore`, `K8sHelper.ResourceOperation`, `CreateExternalRGWService`, and kubectl JSONPath service lookup.

Risks: endpoint lookup uses cluster IP and fixed port 80, while TLS-enabled stores may use secure ports elsewhere. The create path always creates an external service after RGW readiness, so cleanup must remove it through broader cluster cleanup. The code comment explicitly notes weak error handling for endpoint lookup.

Test signals: RGW pod readiness, service endpoint reachability, object store deletion and pod disappearance, plus S3/Swift client operations are the meaningful checks.
