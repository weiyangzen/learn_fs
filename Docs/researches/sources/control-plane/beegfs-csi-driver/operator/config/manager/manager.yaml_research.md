<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manager/manager.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/manager/manager.yaml

## Purpose
Defines the namespace and Deployment for the BeeGFS CSI driver operator manager.

## Important APIs, Types, And Functions
Runs `/manager` with `--leader-elect` and `--metrics-bind-address=0.0.0.0:8443`, sets liveness/readiness probes on 8081, passes `BEEGFS_CSI_DRIVER_NAMESPACE` via Downward API, and uses service account `controller-manager`.

## Control Flow
Kustomize namespaces/prefixes it. At runtime, `main.go` uses the namespace env var to limit the controller cache to the deployment namespace.

## State And Persistence
Deployment state persists one replica and manages Pod lifecycle. Operator process state is in-memory except Kubernetes objects it reconciles.

## Dependencies And Integration Points
Depends on RBAC, metrics service, and controller-runtime health endpoints.

## Risks And Edge Cases
The manager runs as non-root with no privilege escalation, but reconciles privileged driver resources via RBAC. Metrics are exposed on all interfaces and rely on authn/authz filters.

## Test Signals
No direct manifest test; `main.go` and envtest cover manager construction and controller registration.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manager/manager.yaml -->
