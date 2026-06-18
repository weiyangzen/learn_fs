## sources/cloud-native/moby/daemon/build.go

**Purpose:** Supplies daemon callbacks used by BuildKit to log image create/tag events when BuildKit bypasses normal image-service paths.

**Important APIs:** `ImageExportedByBuildkit` logs `events.ActionCreate` for an untagged image ID. `ImageNamedByBuildkit` logs `events.ActionTag` using the descriptor digest and familiar tag string.

**Control flow:** Both functions directly call `daemon.imageService.LogImageEvent`.

**State and persistence:** They do not persist images themselves; they add daemon event records for observability.

**Dependencies and integration:** Integrates BuildKit builder callbacks, distribution references, OCI descriptors, and daemon image-service event logging.

**Risks:** Incorrect ID/reference choice would produce confusing event streams, especially under the containerd image store. These functions assume BuildKit has already completed export/tag operations.

**Test signals:** No direct test in this subset. Event stream integration tests should confirm untagged BuildKit exports and BuildKit-managed tags emit expected daemon events.
