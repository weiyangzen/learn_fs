## sources/cloud-native/moby/daemon/builder/dockerfile/imagecontext.go

**Purpose:** Manages mounted image sources used for base images, cache/export layers, scratch images, and `COPY --from`.

**Important APIs/types:** `getAndMountFunc`, `imageSources`, `newImageSources`, `Get`, `Unmount`, `Add`, `imageMount`, `newImageMount`, `unmount`, `Image`, `NewRWLayer`, and `ImageID`.

**Control flow:** `newImageSources` builds a closure over backend image retrieval with pull policy based on local-only and `PullParent`. `Get` returns cached mounts by image ID/ref or fetches and adds a new mount. `Add` synthesizes image metadata for nil/scratch images and appends to mount cleanup list.

**State and persistence:** Maintains in-memory mount list and image-ID cache. Underlying layers are released by `Unmount`; exported images are created elsewhere.

**Dependencies and integration:** Uses builder backend image retrieval, build options auth/output/platform, internal image type, and container platform defaults.

**Risks:** Mount release failures can leak layer refs. Scratch image OS handling differs on Windows daemon vs target platform. Cache keying only by passed ID/ref can miss aliases until `Add` records actual image ID.

**Test signals:** `imagecontext_test.go` covers scratch add behavior, platform propagation, and Get adding mounts.
