# sources/control-plane/juicefs-csi-driver/pkg/dashboard/cm.go

## Purpose
`cm.go` provides dashboard endpoints for reading/updating the CSI global ConfigMap and computing whether mount pods differ from current configuration.

## Important APIs, Types, And Functions
Handlers are `getCSIConfig`, `putCSIConfig`, and `getCSIConfigDiff`. Utility functions are `DiffConfig` and `DiffConfigWithNode`.

## Control Flow
`getCSIConfig` fetches the global config ConfigMap from the system namespace. `putCSIConfig` binds and validates a ConfigMap named `config.GetGlobalConfigName`, unmarshals `config.yaml`, updates it, then annotates CSI node pods with `juicefs/update-time` to trigger reload behavior. `getCSIConfigDiff` lists upgrade candidate pods filtered by node/uniqueId, computes diffs, paginates `PodDiff` results, and returns them. `DiffConfigWithNode` reconstructs a setting, renews it, and compares the computed hash to the pod hash label.

## State And Persistence
Persistent state includes the global ConfigMap and CSI node pod annotations. Diff operations are read-only and derive state from Pods, PVs, PVCs, Secrets, and Nodes.

## Dependencies And Integration Points
It depends on `config.Config` parsing, `config.RevertSettingWithNode`, `config.JfsSetting.ReNew`, pod/PV/PVC/secret services through `genPodDiffs`, and Kubernetes core APIs.

## Risks
Updating config directly affects all CSI nodes and mount-pod reconciliation. The reload trigger mutates all matching CSI node pods and fails the request on the first update error. Diff correctness depends on reconstructing old and new settings with the same inputs used by the mount controller.

## Test Signals
No direct tests are present. Useful coverage would validate ConfigMap name/config parsing, CSI node annotation mutation, and hash-diff behavior for changed and unchanged settings.
