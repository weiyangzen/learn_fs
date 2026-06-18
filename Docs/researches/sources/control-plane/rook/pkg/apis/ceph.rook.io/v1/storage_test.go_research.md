# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/storage_test.go

Purpose: unit-tests storage-scope node resolution, use-all-devices behavior, device inheritance, node-name lookup, and PVC encryption detection.

Important APIs/types/functions: exercises `StorageScopeSpec.NodeExists`, `ResolveNode`, `AnyUseAllDevices`, `ClearUseAllDevices`, `NodeWithNameExists`, `IsOnPVCEncrypted`, and indirectly `Selection.GetUseAllDevices`. Fixtures use `Node`, `Selection`, `Device`, and `StorageClassDeviceSet`.

Control flow: tests check node existence with no nodes, one node, and multiple nodes. Resolution tests cover nonexistent node returning nil, default values with no cluster defaults, inheritance of cluster device filters/path filters/devices/config, preservation of node-specific filters/devices/config while inheriting missing config, and cluster-level use-all-devices inheritance. Additional tests verify use-all-devices detection at cluster and node levels, clearing that flag everywhere, cluster device inheritance into nodes without devices, preservation of node devices when set, exact node-name existence, and encrypted PVC-backed device-set detection.

State and persistence: local test structs only. Several tests intentionally rely on `ResolveNode` mutating a node inside the storage spec.

Dependencies/integration: depends on testify. These tests protect OSD selection/defaulting behavior used before device discovery and OSD prepare.

Risks: tests do not cover volume claim template inheritance, `NodesByName` sorting, OSD store default/flag helpers, config-map aliasing, or pointer aliasing after inheritance/clear. There is a spelling mismatch in `TestResolveNodeInherentFromCluster`, but it does not affect behavior.

Test signals: good coverage for main node resolution and use-all-devices branches.
