# sources/cloud-native/containerd/core/metadata/namespaces_test.go

Purpose: tests namespace creation and guarded deletion for both empty and non-empty namespace states.

Important APIs and helpers: `TestCreateDelete` uses `NewNamespaceStore`, `Create`, and `Delete`; it also creates a container through `NewContainerStore` and writes snapshotter data directly.

Control flow: table cases create a namespace, optionally populate it with a container and snapshotter bucket, then attempt deletion inside a bbolt update transaction. The empty case expects success; the non-empty case expects an error containing both containers and snapshotter data.

State and persistence: the test writes under the real namespace bucket layout, including `createSnapshotterBucket`, to validate the same emptiness checks used by namespace deletion.

Dependencies and integration: integrates namespace store with container store and snapshotter bucket helpers. Uses `testDB`, `namespaces.WithNamespace`, protobuf `Any`, and testify assertions.

Risks: assertion checks error text, so wording changes in `Delete` may require test updates. It does not cover labels, `SetLabel`, duplicate namespace create, or image/blob blockers.

Test signals: focused signal that namespaces cannot be deleted while selected object families remain.
