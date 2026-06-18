# sources/control-plane/rook/pkg/operator/k8sutil/kvstore_test.go

Purpose: tests ConfigMap-backed key-value store behavior.

Important APIs/types/functions: `TestGetValueStoreNotExist`, `TestGetValueKeyNotExist`, `TestGetValue`, `TestSetValueStoreNotExist`, `TestSetValueUpdate`, `TestGetStoreNotExist`, `TestGetStore`, `TestClearStoreNotExist`, `TestClearStore`, and helper `newKVStore`.

Control flow: tests verify NotFound for missing store and missing key, successful get, automatic store creation on set, value update on existing store, whole-store retrieval, idempotent clear of missing store, and delete-on-clear of existing store. `newKVStore` attaches namespace/name to input ConfigMaps, builds a fake client, creates owner info, and returns a store.

State and persistence behavior: fake ConfigMaps persist in the fake client. Tests validate behavior by calling store methods after mutations.

Dependencies/integration: client-go fake client, Kubernetes NotFound helpers, runtime objects, owner refs, and testify.

Risks: tests do not cover `SetValueWithLabels`, owner reference contents, nil `Data` map on existing ConfigMap, update conflicts, or labels on existing-store updates.

Test signals: good coverage for the normal CRUD contract used by operator components that need small persisted key/value state.
