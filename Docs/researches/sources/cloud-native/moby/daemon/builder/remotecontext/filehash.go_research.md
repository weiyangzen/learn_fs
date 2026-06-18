## sources/cloud-native/moby/daemon/builder/remotecontext/filehash.go

**Purpose:** Builds deterministic per-file hashes for lazy build contexts using tar header metadata plus file content writes.

**Important APIs/types:** `NewFileHash` creates a hash initialized with a tarsum V1 header. `tarsumHash` embeds `hash.Hash` and overrides `Reset` to reapply the header.

**Control flow:** For symlinks, readlink target is included in the archive header. `archive.FileInfoHeader` and security xattrs populate tar metadata, then `tarsum.WriteV1Header` seeds the SHA-256 hash.

**State and persistence:** No persistence. Returned hash object accumulates data written by callers and can reset to the header-initialized state.

**Dependencies and integration:** Used by remote context lazy sources to produce cache keys compatible with tar archive contexts.

**Risks:** Header selection must stay compatible with tarsum V1. Security xattr read failures propagate and can break hashing.

**Test signals:** Tarsum and remotecontext hash tests outside this file exercise hash behavior. Direct tests for xattrs/symlinks would be valuable.
