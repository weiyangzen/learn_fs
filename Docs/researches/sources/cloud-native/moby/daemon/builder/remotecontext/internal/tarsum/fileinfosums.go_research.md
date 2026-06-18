## sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/fileinfosums.go

**Purpose:** Defines sortable/accessor structures for per-file tar checksum metadata.

**Important APIs/types:** `FileInfoSumInterface`, `fileInfoSum`, `FileInfoSums`, `GetFile`, `GetAllFile`, `GetDuplicatePaths`, `Len`, `Swap`, `SortByPos`, `SortByNames`, `SortBySums`, and sort adapters `byName`, `bySum`, `byPos`.

**Control flow:** Lookup is case-insensitive on Windows for `GetFile`. Sorting by name uses original tar position to break ties. Sorting by sums uses position only for duplicate paths to preserve deterministic duplicate handling.

**State and persistence:** In-memory slice of file checksum records generated while reading tar streams.

**Dependencies and integration:** Used by `tarSum.Sum`, archive context `Hash`, and tests. Runtime GOOS affects matching behavior.

**Risks:** Sorting mutates the slice in place; callers must understand ordering changes. Windows case-insensitive lookup can return a different casing's first match.

**Test signals:** `fileinfosums_test.go` covers sorting behavior.
