## sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/builder_context.go

**Purpose:** Extends `TarSum` with removal semantics needed for `.dockerignore` processing during builder context setup.

**Important APIs:** `BuilderContext` interface embeds `TarSum` and adds `Remove(string)`. `(*tarSum).Remove` deletes all sums matching a filename.

**Control flow:** `Remove` iterates the `sums` slice and splices out every entry with the requested name, continuing because duplicate path entries can exist.

**State and persistence:** Mutates in-memory tarsum file list only; it does not edit tar bytes or filesystem contents.

**Dependencies and integration:** Used conceptually by builder context filtering; archive-backed context has a separate `Remove` implementation that deletes files from extracted root.

**Risks:** Removing while ranging over a slice can skip adjacent duplicate entries after splice; tests should guard duplicate behavior. Matching is exact and not Windows case-insensitive here.

**Test signals:** `builder_context_test.go` covers nonexistent removal and removing duplicate entries.
