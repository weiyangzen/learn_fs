## sources/cloud-native/moby/daemon/builder/backend/backend.go

**Purpose:** Exposes build functionality to the API router and selects between classic Dockerfile builder and BuildKit. It also handles tag application, squashing, cache prune, cancellation, and BuildKit gRPC registration.

**Important APIs:** `ImageComponent` abstracts image tagging/squashing. `Builder` abstracts classic build execution. `Backend` stores classic builder, BuildKit builder, image component, and events service. `NewBackend`, `RegisterGRPC`, `Build`, `PruneCache`, `Cancel`, and `squashBuild` are the main entry points.

**Control flow:** `Build` parses tags, checks `options.Version`, runs BuildKit or classic builder, optionally squashes the result, emits aux image ID after squashing, prints classic-builder success text, and tags non-BuildKit images. `PruneCache` delegates to BuildKit and logs a builder prune event.

**State and persistence:** Build results create/tag/squash images via downstream components. Backend itself is stateless beyond component references. Prune emits event metadata with reclaimed bytes.

**Dependencies and integration:** Integrates API `buildbackend.BuildConfig`, BuildKit `builder-next`, daemon image component, events, distribution references, and classic builder result objects.

**Risks:** `PruneCache` and `Cancel` assume `buildkit` is non-nil. Classic tag printing only occurs for non-BuildKit builds. Squash must preserve correct base image ID from `FromImage`.

**Test signals:** Adjacent tag tests are not listed here, but `tag.go` logic is testable. Backend integration needs coverage for BuildKit vs classic selection, nil results, squash aux emission, duplicate tags, and prune events.
