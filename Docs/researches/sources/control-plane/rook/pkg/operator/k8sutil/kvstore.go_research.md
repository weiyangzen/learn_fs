# sources/control-plane/rook/pkg/operator/k8sutil/kvstore.go

Purpose: implements a simple ConfigMap-backed key-value store abstraction.

Important APIs/types/functions: `ConfigMapKVStore`, `NewConfigMapKVStore`, `GetValue`, `SetValue`, `SetValueWithLabels`, `GetStore`, and `ClearStore`.

Control flow: `GetValue` gets the ConfigMap and returns a NotFound error if the key is absent. `SetValue` delegates to `SetValueWithLabels`. `SetValueWithLabels` gets the ConfigMap; on NotFound it creates one with initial data, optional labels, and controller owner reference; otherwise it mutates `Data[key]` and updates the ConfigMap. `GetStore` returns the ConfigMap `Data` map. `ClearStore` deletes the ConfigMap and ignores NotFound.

State and persistence behavior: persists data in Kubernetes ConfigMaps in the configured namespace. Owner references are applied only when creating a new store.

Dependencies/integration: depends on client-go CoreV1 ConfigMaps, Kubernetes NotFound errors, schema group resource for key-not-found, and k8sutil `OwnerInfo`.

Risks: updating an existing ConfigMap assumes `cm.Data` is non-nil; a nil Data map would panic on assignment. No conflict retry on update. `GetStore` returns the underlying map from the fetched object, so callers can mutate the map locally without persistence unless they call Set/Update.

Test signals: `kvstore_test.go` covers missing store/key, get, set-create, set-update, get-store, and clear-store behavior.
