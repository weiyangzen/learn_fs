## sources/cloud-native/moby/daemon/internal/layer/ro_layer.go

Purpose: Implements immutable layer objects, retained references, tar stream verification, and metadata serialization helpers.

Important APIs/types: `roLayer` stores chain ID, diff ID, parent, graphdriver cache ID, size, store, optional distribution descriptor, reference count, and retained reference set. Methods implement `Layer`: `TarStream`, `TarStreamFrom`, `ChainID`, `DiffID`, `Parent`, `Size`, `DiffSize`, `Metadata`, plus `CacheID`, reference helpers, `depth`, `storeLayer`, `newVerifiedReadCloser`, and `verifiedReadCloser`.

Control flow: `TarStream` reconstructs the original tar from tar-split metadata and graphdriver files, then wraps it in a digest verifier that checks against `diffID` at EOF. `TarStreamFrom` returns a graphdriver diff from an ancestor cache ID but explicitly does not guarantee exact original tar bytes. `Size` recursively adds parent sizes. `getReference` creates a `referencedCacheLayer` and records it. `storeLayer` writes diff, size, cache ID, non-empty descriptor, and parent into a metadata transaction. `verifiedReadCloser.Read` hashes bytes as they pass and errors at EOF if digest verification fails.

State and persistence: Reference state is in memory; serialized metadata is persisted by `storeLayer`. Tar verification protects against layerdb/driver tampering.

Dependencies and integration: Used by image store layer retention, tar export, distribution upload, and layer store registration/release.

Risks: Reference helpers assume external locking by `layerStore`. `TarStreamFrom` can produce non-verifiable streams and must not be used for content identity. Verification errors only appear when the stream is fully read to EOF.

Test signals: Layer tests cover tar stability, duplicate references, release behavior, and verification failure.
