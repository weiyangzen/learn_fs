<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/refmanager.go -->
## sources/cloud-native/buildkit/solver/llbsolver/file/refmanager.go

Purpose: adapts BuildKit cache refs into file operation mounts and commits mutable file-op results.

Important APIs and types: `NewRefManager`, `RefManager`, `Prepare`, `Commit`, and `Mount` methods `Mountable`, `Release`, `IsFileOpMount`, `Readonly`.

Control flow: `Prepare` accepts an immutable ref or nil. For readonly immutable refs it returns a readonly mount directly. Otherwise it creates a mutable ref from the input with retain policy and description, mounts it, and rolls back cache policy/release on failure. `Commit` requires a `Mount` with an active mutable ref, commits it to an immutable ref, releases on commit failure, and clears `mr`.

State and persistence: creates and commits cache mutable refs through `cache.Manager`, which persists snapshot/cache state externally. `Mount` holds current mountable, mutable ref, and readonly flag.

Dependencies and integration: integrates file op solver with BuildKit cache, sessions, snapshot mountables, and logging.

Risks and test signals: failure cleanup is important to avoid orphan mutable refs; committing a readonly mount is invalid. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/file/refmanager.go -->
