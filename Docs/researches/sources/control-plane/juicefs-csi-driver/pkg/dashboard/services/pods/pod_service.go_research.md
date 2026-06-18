# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/pod_service.go

## Purpose
This file implements the uncached pod service and shared pod relationship helpers used by both cached and uncached dashboard modes.

## Important APIs, Types, And Functions
It defines `podService` and methods for listing PVCs/PVs of a pod, mount pods of app pods, CSI node pods, pod node, app/system pods, node mount pods, all mount pods, app pods of a mount pod, batch pods, and upgrade-eligible pods.

## Control Flow
PVC/PV helper methods walk pod volumes and bound PVCs. Mount-pod relation methods select mount pods by labels and node, then compare mount-pod annotation targets against app pod UIDs through `utils.GetTargetUID`. App pod listing first searches mount-mode app pods by `common.UniqueId` label and falls back to injected sidecar label. System pod listing uses pod-type label expressions. Upgrade listing selects mount pods by label, optional unique ID and node, then calls `resource.FilterPodsToUpgrade`.

## State And Persistence
The service is stateless aside from Kubernetes clients/config. It reads Kubernetes pods, PVCs, PVs, and nodes, but does not mutate them.

## Dependencies And Integration Points
It depends on controller-runtime client list/get operations, Kubernetes label and field selectors, dashboard utilities, `config.Namespace`, and `resource.FilterPodsToUpgrade`.

## Risks
Uncached app listing only falls back to sidecar pods when no mount-mode app pods are found at all, so mixed clusters may omit sidecar app pods. Several list methods return all selected Kubernetes objects without filtering to JuiceFS PVs after relation expansion. `getCSINode` requires at least one CSI node pod and returns an error otherwise.

## Test Signals
No tests are present. Useful tests would cover mixed app-pod modes, annotation UID parsing, node field selector behavior, and upgrade pod filtering.
