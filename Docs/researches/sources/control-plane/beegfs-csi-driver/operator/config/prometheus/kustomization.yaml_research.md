<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/prometheus/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/prometheus/kustomization.yaml

## Purpose
Optional Prometheus overlay entry point.

## Important APIs, Types, And Functions
Includes only `monitor.yaml`.

## Control Flow
When uncommented in the default overlay, kustomize adds a ServiceMonitor to the install set.

## State And Persistence
No local state; rendered ServiceMonitor persists if the Prometheus Operator CRD exists.

## Dependencies And Integration Points
Depends on Prometheus Operator APIs and the manager metrics service.

## Risks And Edge Cases
Applying this without the ServiceMonitor CRD installed fails. The monitor's named port must match the metrics Service.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/prometheus/kustomization.yaml -->
