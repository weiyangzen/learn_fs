## sources/cloud-native/moby/daemon/builder/dockerfile/mockbackend_test.go

**Purpose:** Provides mock implementations of builder backend, image cache, image, and layer interfaces for Dockerfile unit tests.

**Important APIs/types:** `MockBackend` implements attach, create, remove, commit, start, wait, workdir, copy, get image/layer, make cache, and create image methods. `mockImage`, `mockImageCache`, `mockLayer`, and `mockRWLayer` implement image/cache/layer contracts.

**Control flow:** Most methods return preconfigured fields or nil values. `mockImageCache.GetCache` returns a configured cache ID. Layers expose fixed roots/digests and commit behavior.

**State and persistence:** In-memory mock fields; no daemon state. It simulates image IDs and layer lifecycle for tests.

**Dependencies and integration:** Used by dispatcher, evaluator, imagecontext, and internals tests.

**Risks:** Mock permissiveness can hide backend contract mistakes. Methods that no-op should be used carefully when tests need lifecycle assertions.

**Test signals:** Enables isolated tests; its existence is not a behavioral test itself, but it defines what unit tests can observe.
