# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/storage.go

Purpose: implements storage-selection helpers for Ceph cluster storage specs, including device-selection inheritance, node lookup, OSD store defaults, and PVC encryption detection.

Important APIs/types/functions: `StoreType`, `StoreTypeBlueStore`, `StoreTypeBlueStoreRDR`, `StorageScopeSpec.AnyUseAllDevices`, `ClearUseAllDevices`, `NodeExists`, `ResolveNode`, `resolveNodeSelection`, `resolveNodeConfig`, `NodeWithNameExists`, `Selection.GetUseAllDevices`, `resolveString`, `newBool`, `NodesByName` (`Len`, `Swap`, `Less`), `StorageScopeSpec.IsOnPVCEncrypted`, `GetOSDStore`, and `GetOSDStoreFlag`.

Control flow: `AnyUseAllDevices` checks cluster-level selection first, then node-level selections. `ClearUseAllDevices` creates one false pointer and assigns it to cluster and all node selections. `ResolveNode` finds a node by name, initializes its config map when nil, then fills missing node selection and config from cluster-level defaults. Selection resolution inherits `UseAllDevices`, device filter, device path filter, devices, and volume claim templates when node-specific values are absent, defaulting use-all-devices to false. Config resolution copies any missing parent config keys without overwriting node-specific keys. Store helpers default to `bluestore` and return either raw type or `--<type>`.

State and persistence: mutates `StorageScopeSpec.Nodes[i]` in place during `ResolveNode`, including inherited pointers/slices/maps. No direct persistence, but resolved specs drive later Ceph OSD reconciliation.

Dependencies/integration: depends on `fmt`. Integrates with cluster CRD storage reconciliation for device discovery, OSD prepare jobs, PVC-backed OSDs, and daemon command-line flags.

Risks: `ResolveNode` returns a pointer into the `Nodes` slice and mutates it; callers must account for side effects. Inherited `UseAllDevices` pointer may alias the cluster-level pointer. `ClearUseAllDevices` assigns the same false pointer to all nodes. `resolveString` cannot distinguish intentionally empty from unset. `NodeExists` and `NodeWithNameExists` duplicate behavior. `GetOSDStoreFlag` uses `fmt.Sprintf` for simple prefixing.

Test signals: `storage_test.go` covers node lookup, missing node resolution, default/inherited/specific selection and config, use-all-devices checks and clearing, device inheritance, node-name existence, and PVC encryption detection.
