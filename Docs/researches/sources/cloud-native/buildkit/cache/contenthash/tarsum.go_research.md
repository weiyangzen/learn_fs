# sources/cloud-native/buildkit/cache/contenthash/tarsum.go

Purpose: writes Docker legacy V1 tarsum-compatible tar header fields into cache hash streams.

Important APIs/types/functions: `WriteV1TarsumHeaders`, `v0TarHeaderSelect`, and `v1TarHeaderSelect`.

Control flow: `WriteV1TarsumHeaders` selects ordered V1 tar header key/value pairs and writes them to an `io.Writer`. V0 selection includes core tar metadata fields. V1 extends V0 by sorting PAX record keys and adding each key/value pair.

State and persistence behavior: no state; its output contributes to file digests persisted in contenthash records.

Dependencies and integration points: used by `tarsumHash.Reset` in `filehash.go`. Depends on archive/tar and io.

Risks: legacy compatibility is the point; changing field order or selected fields changes every file digest. PAX/xattr ordering must remain stable for deterministic hashes.

Test signals: golden contenthash digests in `checksum_test.go` detect changes in header hashing behavior.
