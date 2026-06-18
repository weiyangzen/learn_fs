## sources/cloud-native/moby/daemon/builder/dockerfile/internals_test.go

**Purpose:** Tests core builder internals around Dockerfile reading, run-config copying, and image export.

**Important APIs:** Tests include empty Dockerfile, symlink Dockerfile, Dockerfile outside context, missing Dockerfile, `copyRunConfig`, deep-copy behavior, mock RW/RO layers, and `exportImage`.

**Control flow:** Filesystem fixtures validate remote context Dockerfile lookup/parse behavior. Config tests mutate copies to confirm original configs are not aliased. Export tests validate image/layer creation path with mocks.

**State and persistence:** Uses temporary dirs and mock layers/images; no real daemon state.

**Dependencies and integration:** Bridges remotecontext behavior and Dockerfile builder internals.

**Risks:** Mock export cannot fully validate content store behavior or actual layer release ordering.

**Test signals:** Good regression signal for path safety, Dockerfile parsing errors, and run-config copy depth.
