## sources/cloud-native/moby/daemon/builder/dockerfile/copy_unix.go

**Purpose:** Provides Unix-specific ADD/COPY destination normalization, wildcard detection, permission fixing, and source path validation.

**Important APIs:** `fixPermissions` walks the source tree and `Lchown`s corresponding destination paths, optionally skipping an existing destination root. `normalizeDest` resolves relative destinations under WORKDIR while preserving trailing slashes. `containsWildcards` honors backslash escaping. `validateCopySourcePath` is a no-op on Unix.

**Control flow:** Permission fixing walks source paths and maps each relative path to the destination. Destination normalization uses POSIX path semantics even before conversion to daemon filesystem paths.

**State and persistence:** Mutates filesystem ownership on copied files/directories in the RW layer.

**Dependencies and integration:** Used by common copy execution in `copy.go` and `internals.go`; depends on `os`, `filepath`, and path semantics.

**Risks:** Chown must avoid changing pre-existing directory roots unless override is requested. Wildcard escaping differs from Windows and impacts matching compatibility.

**Test signals:** Direct tests for Unix normalizeWorkdir exist in dispatcher Unix tests; copy-specific Unix chown and wildcard behavior need integration tests.
