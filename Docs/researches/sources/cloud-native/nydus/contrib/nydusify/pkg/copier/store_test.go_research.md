# sources/cloud-native/nydus/contrib/nydusify/pkg/copier/store_test.go

Purpose: validates the copier store wrapper's `Info` fallback semantics.

Important fixtures/APIs: `stubStore` implements enough of `content.Store` for tests; tests call `newStore` and `Info`.

Control flow and state: tests cover fallback to remote descriptors on base-store not found, preservation of unexpected base-store errors, preference for base-store info when present, not-found when neither base nor remote descriptors match, construction of the wrapper, multiple remote descriptors, and empty remote descriptor lists.

Dependencies and integration points: containerd content interfaces, errdefs, digest, and OCI descriptors.

Risks and test signals: coverage is narrow but precise for `Info`. Other embedded store methods are not customized and only rely on the underlying store. Tests do not validate behavior when remote descriptor sizes are zero or when duplicate remote descriptors exist.
