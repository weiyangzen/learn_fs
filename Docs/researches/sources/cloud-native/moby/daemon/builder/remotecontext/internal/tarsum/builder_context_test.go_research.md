## sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/builder_context_test.go

**Purpose:** Tests `tarSum.Remove` behavior.

**Important APIs:** `TestTarSumRemoveNonExistent` and `TestTarSumRemove` operate on `tarSum.sums`.

**Control flow:** Tests create in-memory `FileInfoSums`, remove names, and compare expected remaining entries.

**State and persistence:** In-memory only.

**Dependencies and integration:** Protects .dockerignore-oriented tarsum filtering semantics.

**Risks:** Coverage should ensure duplicate removal does not skip adjacent entries; this is important because tar archives can contain duplicate paths.

**Test signals:** Direct signal for the only behavior in `builder_context.go`.
