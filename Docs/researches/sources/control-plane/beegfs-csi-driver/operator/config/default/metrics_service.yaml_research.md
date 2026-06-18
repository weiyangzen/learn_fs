<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/default/metrics_service.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/default/metrics_service.yaml

## Purpose
Exposes the operator manager metrics endpoint as a Kubernetes Service.

## Important APIs, Types, And Functions
Service `controller-manager-metrics-service` targets TCP port 8443 and selects pods labeled `control-plane: controller-manager`.

## Control Flow
Kustomize prefixes and namespaces it. Prometheus ServiceMonitor can select the service if enabled.

## State And Persistence
Cluster Service object persists virtual networking state for metrics access.

## Dependencies And Integration Points
Depends on labels in `manager.yaml` and secure metrics server configured in `main.go`.

## Risks And Edge Cases
The Service port lacks a name, while the ServiceMonitor references port `https`; rendered manifests may need a named port for Prometheus Operator compatibility.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/default/metrics_service.yaml -->
