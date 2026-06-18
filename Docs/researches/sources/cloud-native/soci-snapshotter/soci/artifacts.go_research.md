# sources/cloud-native/soci-snapshotter/soci/artifacts.go

Purpose: this file manages the BoltDB metadata index for local SOCI artifacts. It records SOCI index manifests, zTOC layer artifacts, and prefetch artifacts so CLI and daemon flows can discover, push, clean, and relate artifacts to images and layers.

Important APIs and types: `ArtifactsDb` wraps `*bolt.DB`. `ArtifactEntry` stores size, digest, original content digest, image digest, platform, location, entry type, media type, artifact type, creation time, and span size. `ArtifactsDbPath` resolves the default DB path. `NewDB` initializes a package-level singleton. Public methods include `Walk`, `SyncWithLocalStore`, `RemoveOldArtifacts`, `GetArtifactEntry`, `GetArtifactType`, `RemoveArtifactEntryByIndexDigest`, `GetArtifactEntriesByImageDigest`, and `WriteArtifactEntry`.

Control flow: `SyncWithLocalStore` removes DB entries whose descriptors no longer exist in the blob store, then scans the local content store path for new SOCI index blobs. `addNewArtifacts` walks files, ignores tiny/config-like content, decodes candidate indexes, verifies media/artifact/subject fields, derives platform from the containerd content store, writes an index entry, and writes zTOC entries from the index blobs. `WriteArtifactEntry` creates per-digest buckets under `soci_artifacts`; `loadArtifact` reverses that encoding.

State and persistence: BoltDB schema is bucket-oriented: root `soci_artifacts`, child bucket per artifact digest, scalar keys for encoded size/span size, digests, platform, location, type, media type, artifact type, and creation time. Integer fields use varint encoding from `util/dbutil`.

Dependencies and integration points: integrates config defaults, SOCI `store.Store`, containerd content/images/platforms, OCI descriptors, bbolt, errdefs, and `soci_index.go` serialization.

Risks: `NewDB` is a package-level `sync.Once` singleton, so tests and multi-root callers must reset or cannot open different DBs in one process. `Walk` suppresses missing root bucket errors by returning nil, which makes an absent DB look empty. `addNewArtifacts` guesses digest algorithm by filename length, assumes `images.Platforms` returns at least one platform, and silently ignores decode failures. `RemoveOldArtifacts` queues bucket deletion to avoid Bolt iteration mutation hazards.

Test signals: `artifacts_test.go` covers path derivation, singleton failure behavior, read/write round trips, atomic bucket helper operations, and index-entry filtering by original digest.
