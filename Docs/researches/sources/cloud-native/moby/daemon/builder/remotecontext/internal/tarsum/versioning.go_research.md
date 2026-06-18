# sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/versioning.go

## Purpose
Defines TarSum algorithm versions and the ordered tar-header field selection used to produce stable per-entry hashes. It preserves the original `tarsum` behavior while adding a v1/dev selector that ignores mtime and includes sorted xattrs.

## Important APIs, Types, And Functions
Exports `Version`, constants `Version0`, `Version1`, `VersionDev`, `WriteV1Header`, `VersionLabelForChecksum`, `GetVersions`, `Version.String`, and `GetVersionFromTarsum`. Internal selectors are `v0TarHeaderSelect`, `v1TarHeaderSelect`, `tarHeaderSelector`, `tarHeaderSelectFunc`, `registeredHeaderSelectors`, and `getTarHeaderSelector`.

## Control Flow
`GetVersionFromTarsum` cuts at `+` and looks up the version label. `v0TarHeaderSelect` emits fixed metadata fields including mtime. `v1TarHeaderSelect` gathers `SCHILY.xattr.` PAX records, overlays deprecated `Header.Xattrs` values when both exist, appends xattr-only entries, sorts by key, copies v0 fields except mtime, then appends xattrs.

## State And Persistence
State is static maps from version enum to label and selector. No persistent storage is touched, but selector output defines persistent checksum compatibility for stored layer/build-cache metadata.

## Dependencies And Integration Points
Used by `NewTarSum`, file hashing helpers, and tests. Depends on Go `archive/tar` header semantics, including deprecated `Xattrs`, and mirrors archive/tar precedence between PAX and xattr maps.

## Risks And Test Signals
Map iteration makes `GetVersions` unordered. Changing field order or xattr precedence changes every digest for affected archives. Tests in `versioning_test.go` and `tarsum_test.go` catch labels, version lookups, and xattr selector order.
