# sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_controller_test.go

Purpose: unit-tests low-level controller cache update semantics and the deletion predicate for `VolumeSnapshotContent` objects.

Important APIs/functions: helper `storeVersion`, `TestControllerCache`, `TestControllerCacheParsingError`, and `TestShouldDelete`. The tests use `utils.StoreObjectUpdate`, a client-go cache store, `newContent` test fixtures, and deletion annotations/finalizers from the controller package.

Control flow: `storeVersion` creates a content object with a specific `ResourceVersion`, stores it, and validates both the return value and cache contents. `TestControllerCache` exercises first insert, same-version update, newer update, stale older update rejection, and numeric ordering where `"10"` must sort after `"2"`. `TestShouldDelete` constructs timestamp/annotation/binding scenarios and verifies the controller's boolean deletion gate.

State and persistence: all state is in-memory fake content and cache entries. The tests do not hit Kubernetes API clients or CSI mocks.

Dependencies and integration: depends on test fixture constructors from the sidecar test package, snapshot CRD types, client-go cache, and metadata utilities. It validates behavior consumed by `syncContentByKey` and `syncContent`.

Risks and test signals: strong signal for stale informer-event suppression and resource-version parsing. Deletion predicate coverage is narrow but covers nil deletion timestamp, unbound pre-provisioned content, explicit delete annotation, and fallback no-delete cases; it does not cover the create-in-progress annotation branch directly.
