# sources/cloud-native/buildkit/cache/contenthash/filehash.go

Purpose: creates per-file hashers that encode tar-style file metadata plus optional file content for BuildKit cache keys.

Important APIs/types/functions: `NewFileHash`, `NewFromStat`, `tarsumHash` with `Reset`, `Write`, `Sum`, and `statInfo` implementing `os.FileInfo`.

Control flow: `NewFileHash` reads symlink targets, builds an fsutil `Stat`, normalizes symlink mode, fills Unix-specific fields via `setUnixOpt`, then calls `NewFromStat`. `NewFromStat` clears socket/irregular bits, converts stat metadata to a tar header, attaches device IDs, uid/gid, and xattrs, initializes a cachedigest file hash, and writes V1 tarsum headers on reset. File contents are added later by callers writing to the returned hash.

State and persistence behavior: no direct persistence. The resulting digest is stored in `CacheRecord.Digest` by `checksum.go`. `tarsumHash.Write` increments header size as bytes are written.

Dependencies and integration points: depends on tar headers, fsutil stat types, cachedigest, and OS-specific `setUnixOpt`. `prepareDigest` in `checksum.go` uses this for actual mounted files; tests use `NewFromStat` for synthetic change streams.

Risks: metadata normalization defines cache-key compatibility. Ignoring socket/irregular bits and using empty tar header names are deliberate choices; changing them alters all cache digests. Xattr ordering depends on map iteration through tar PAX records unless downstream hashing sorts records.

Test signals: golden digests in `checksum_test.go` validate file, symlink, directory, hardlink, xattr-capable stat hashing indirectly.
