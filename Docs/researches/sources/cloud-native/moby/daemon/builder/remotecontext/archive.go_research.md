## sources/cloud-native/moby/daemon/builder/remotecontext/archive.go

**Purpose:** Converts a build-context tar stream into a `builder.Source` backed by a temporary extracted directory and deterministic tarsum hashes.

**Important APIs/types:** `archiveContext`, `Close`, `convertPathError`, `modifiableContext`, `FromArchive`, `Root`, `Remove`, `Hash`, and `normalize`.

**Control flow:** `FromArchive` creates a temp dir, decompresses the stream, wraps it in tarsum, untars into the temp root, stores file sums, and returns the context. `Hash` normalizes/scopes paths, resolves symlinks inside root, finds the relative tarsum entry, and falls back to path for legacy cases.

**State and persistence:** Temporary extracted context is removed by `Close`. `sums` keeps per-file archive hashes in memory and drives cache keys.

**Dependencies and integration:** Used by local archive, URL archive, and git contexts. Depends on chroot untar, compression, longpath temp dirs, symlink scope checks, and internal tarsum.

**Risks:** Path normalization and symlink scoping are security-critical. Hash fallback may preserve compatibility but can mask missing tarsum entries. Caller must close context to remove temp directories.

**Test signals:** Remotecontext/tarsum tests outside the listed file set cover hash/remove/close behavior; internals tests cover Dockerfile path safety.
