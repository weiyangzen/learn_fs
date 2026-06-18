## sources/cloud-native/moby/daemon/builder/remotecontext/git.go

**Purpose:** Builds a `builder.Source` from a Git URL by cloning to a temp directory, tarring it, and feeding it through archive context creation.

**Important APIs:** `MakeGitContext(gitURL)` calls `git.Clone` with isolated config, archives the clone root with no compression, defers tar close and clone deletion, and returns `FromArchive(c)`.

**Control flow:** Clone first, tar second, defer cleanup/logging, then create an archive-backed source whose own temp dir survives until source close.

**State and persistence:** Temporary Git clone is removed before return completes. The returned source has its own extracted temporary directory and tarsum state.

**Dependencies and integration:** Connects remotecontext detection with `remotecontext/git` utility and archive/tarsum source handling.

**Risks:** Two-stage temp handling must avoid deleting data before `FromArchive` finishes. Clone cleanup errors are logged only. Isolated Git config reduces host config influence.

**Test signals:** `git/gitutils_test.go` covers clone parsing/checkout behavior; archive context tests cover returned source semantics.
