## sources/cloud-native/moby/daemon/builder/builder.go

**Purpose:** Defines shared interfaces between daemon build implementations and Dockerfile evaluator code.

**Important APIs/types:** `Source` supplies `Root`, `Close`, and deterministic `Hash`. `Backend` combines image, execution, commit, workdir, create-image, and image-cache operations. `ImageBackend`, `ExecBackend`, `Result`, `ImageCacheBuilder`, `ImageCache`, `Image`, `ROLayer`, and `RWLayer` define the classic builder dependency boundary.

**Control flow:** This file has no executable orchestration; it is a contract package.

**State and persistence:** Implementations behind these interfaces manage images, layers, containers, cache entries, and temporary build contexts. The interfaces explicitly model layer release/commit and source cleanup.

**Dependencies and integration:** Used by Dockerfile builder, daemon image/container backends, remote contexts, and tests/mocks. It decouples evaluator logic from concrete daemon services.

**Risks:** Interface shape is broad; changes affect many packages. Resource lifecycle methods (`Close`, `Release`, `Commit`) are critical because leaks occur outside this package.

**Test signals:** Mock implementations in `mockbackend_test.go` exercise much of this surface. Compile-time conformance from real daemon components is an important signal.
