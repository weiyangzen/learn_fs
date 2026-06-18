## sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/fileinfosums_test.go

**Purpose:** Tests sorting behavior for `FileInfoSums`.

**Important APIs:** `newFileInfoSums` helper and `TestSortFileInfoSums` exercise `SortByNames`, `SortBySums`, and `SortByPos`.

**Control flow:** Creates deterministic in-memory sums and validates order after each sort.

**State and persistence:** In-memory only.

**Dependencies and integration:** Protects deterministic tarsum order used for aggregate checksums.

**Risks:** Does not cover Windows case-insensitive `GetFile` or duplicate-path edge cases in depth.

**Test signals:** Good signal for ordering primitives that affect cache checksum stability.
