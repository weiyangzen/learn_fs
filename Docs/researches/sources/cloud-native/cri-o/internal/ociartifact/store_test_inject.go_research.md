# sources/cloud-native/cri-o/internal/ociartifact/store_test_inject.go

Purpose: test-only injection hooks for replacing an `ociartifact.Store`'s concrete libartifact store and implementation with mocks.

Important APIs/types/functions: `SetFakeStore(LibartifactStore)`, `SetFakeImpl(Impl)`, and `FakeLibartifactStore` embedding the generated mock libartifact store.

Control flow: the setters directly assign private fields on `Store`; there is no validation or cleanup. Test code calls them after `NewStore` to route later store operations through gomock expectations.

State and persistence behavior: mutates only in-memory `Store` fields. The `//go:build test` tag prevents this test seam from existing in normal builds.

Dependencies and integration points: imports `github.com/cri-o/cri-o/test/mocks/ociartifact`. It integrates with `store_test.go` and with CRI-O's test build profile.

Risks: if `Store` internals change, these helpers can silently diverge from production construction. Because setters bypass invariants, they must remain limited to test builds.

Test signals: useful because artifact classification and pinning tests can isolate store logic from registry, filesystem, and libartifact behavior.
