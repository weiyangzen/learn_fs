# sources/cloud-native/nydus/src/bin/nydus-image/validator.rs

## Purpose
`validator.rs` validates that a RAFS bootstrap can be loaded and traversed, optionally prints inode/chunk details, and returns referenced blob metadata for the `nydus-image check` command.

## Important APIs, Types, And Functions
`Validator` owns a loaded `RafsSuper`. `Validator::new` loads a bootstrap from a path and `ConfigV2`. `Validator::check` builds a `Tree` from the superblock, optionally prints every inode and chunk, then returns blob infos, compressor, and RAFS version.

## Control Flow
The command path constructs a validator, calls `check(verbose)`, and then formats blob details in `main.rs`. Inside `check`, `Tree::from_bootstrap` performs the structural metadata load. A DFS pre-order walk is used mainly to force traversal and to print verbose content. Compressor and RAFS version are read from metadata after traversal.

## State And Persistence
The module is read-only. Its only state is the loaded `RafsSuper` in memory. Verbose mode writes to stdout; the caller may write output JSON.

## Dependencies And Integration Points
It depends on `RafsSuper`, `Tree`, `BlobInfo`, `ConfigV2`, `compress::Algorithm`, and `RafsVersion`. It is integrated by `nydus-image check`, which also sets legacy `blob_accessible` behavior.

## Risks
Validation depth depends on what `Tree::from_bootstrap` and `walk_dfs_pre` check; this file does not independently validate blob availability or chunk payload integrity. `try_into().unwrap()` on metadata version assumes the RAFS loader never returns an unsupported version. Verbose printing can be large for big images.

## Test Signals
Unit tests cover invalid bootstrap rejection and successful RAFS v6 fixture validation with expected blob id, zstd compressor, and version. Broader coverage should include corrupt metadata, RAFS v5, multi-blob images, missing blobs, and verbose traversal.
