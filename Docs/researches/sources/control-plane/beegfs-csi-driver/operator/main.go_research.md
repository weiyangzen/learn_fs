<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/main.go -->
# sources/control-plane/beegfs-csi-driver/operator/main.go

## Purpose
Entry point for the BeeGFS CSI driver operator manager.

## Important APIs, Types, And Functions
Registers Kubernetes and BeegfsDriver schemes, parses flags for metrics/probes/leader election/HTTP2, creates controller-runtime manager, configures namespace-scoped cache from `BEEGFS_CSI_DRIVER_NAMESPACE`, secure metrics with authn/authz filters, webhook port 9443, health/readiness checks, and registers `BeegfsDriverReconciler`.

## Control Flow
Process initializes logging, optionally disables HTTP/2 in TLS config, builds manager, registers controller and health checks, then starts until signal cancellation.

## State And Persistence
Runtime state is in-memory manager/cache/controller state. Persistent effects happen through the reconciler.

## Dependencies And Integration Points
Integrates controller-runtime cache, metrics server, webhook server, healthz, zap logging, and operator API scheme. Deployment passes namespace env var via Downward API.

## Risks And Edge Cases
If namespace env var is absent, the cache watches all namespaces. Secure metrics require RBAC for TokenReview/SubjectAccessReview. HTTP/2 is disabled by default due to documented CVEs.

## Test Signals
No direct unit test of main; envtest separately instantiates a manager and registers the reconciler.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/main.go -->
