# sources/control-plane/csi-driver-nfs/charts/v4.13.2/csi-driver-nfs/templates/csi-snapshot-controller.yaml

## Purpose
This template optionally deploys the CSI snapshot controller for v4.13.2 chart installs. It is intended for clusters that do not already provide a snapshot controller.

## Important APIs, Types, and Functions
It emits an `apps/v1` `Deployment` gated by `externalSnapshotter.enabled`, with configurable labels, annotations, replicas, image, image pull secrets, priority class, resources, and scheduling. The controller runs with `--leader-election=true` and `--leader-election-namespace={{ .Release.Namespace }}`.

## Control Flow, State, and Persistence
The Deployment waits at least 15 seconds before readiness, uses a rolling strategy with no surge, and applies Linux node selection plus optional control-plane/master affinity inherited from controller values. Runtime persistence is snapshot object reconciliation and leader-election leases.

## Dependencies and Integration Points
It requires `rbac-snapshot-controller.yaml`, snapshot CRDs, and an external snapshotter image compatible with the CRD schema. It complements the controller Deployment's CSI snapshotter sidecar.

## Risks and Test Signals
Risks are duplicate snapshot controllers, missing CRDs, broad cluster RBAC, and scheduling hidden behind controller affinity settings. Signals are rollout readiness, lease acquisition, no CRD discovery crash, and dynamic snapshot creation/binding.
