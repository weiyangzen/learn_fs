# sources/cloud-native/ostree/src/libostree/ostree-core.h

## Purpose
This public header defines core libostree object constants, metadata GVariant formats, repository mode enums, checksum helpers, content stream parsing/checksumming APIs, structural validators, and commit metadata accessors. It is the central ABI contract for object naming, object validation, content serialization, and commit-level metadata used across the repository, pull, checkout, and verification code.

## Important APIs, Types, And Functions
`OstreeObjectType` enumerates file, dirtree, dirmeta, commit, tombstone, commitmeta, payload-link, and split-xattrs object variants; `OSTREE_OBJECT_TYPE_IS_META()` and `OSTREE_OBJECT_TYPE_LAST` define classification/range checks. `OstreeRepoMode` defines storage modes including archive, bare-user, bare-user-only, and bare-split-xattrs. Public helpers convert checksums between hex/base64/raw/GVariant forms, validate revs, remote names, collection IDs, and parse refspecs. Object-name APIs serialize and deserialize `(checksum, type)` pairs. Content APIs parse archive/raw content and create archive-z2/content streams. Checksum APIs cover `GFile`, fd-relative paths, async checksumming, xattr-aware checksumming, and hardlink breaking. `OstreeChecksumFlags` controls xattr and canonical-permission behavior. Structure validators check object variants and file modes. `OstreeCommitSizesEntry` represents entries in `ostree.sizes` metadata.

## Control Flow, State, And Persistence
The header itself has no executable flow, but it codifies persisted on-disk/wire formats: dirmeta/filemeta/tree/commit/summary GVariant signatures, commit metadata keys, SHA256 lengths, and metadata size limits. Consumers must preserve big-endian GVariant fields and stable metadata key semantics because these formats are persisted in OSTree repositories and exchanged over HTTP.

## Dependencies And Integration Points
It depends on GIO/GVariant, `ostree-types.h`, and `struct stat`. It is included by repository, diff, pull, checkout, and verification modules. The `OSTREE_MAX_METADATA_SIZE` value integrates with fetch logic to limit metadata download/storage abuse.

## Risks And Test Signals
ABI and persisted-format stability are the main risks: changing enum values, GVariant strings, checksum sizes, or metadata keys would break repositories and clients. Tests should cover checksum round trips, invalid refs/remotes/collections, object-name serialization, structural validation for malformed variants, mode-specific xattr/canonical-permission checksums, and backwards compatibility for commit size metadata.
