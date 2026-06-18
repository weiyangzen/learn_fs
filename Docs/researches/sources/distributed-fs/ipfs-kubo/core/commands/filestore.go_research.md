<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/filestore.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/filestore.go

## Purpose

Implements `ipfs filestore` commands for listing, verifying, deleting bad filestore links, and finding duplicate blocks stored both in filestore and main blockstore.

## Important APIs, Types, and Functions

`FileStoreCmd` registers `ls`, `verify`, and `dups`. `lsFileStore`, `verifyFileStore`, and `dupsFileStore` are handlers. `getFilestore` obtains the enabled filestore from the node. `listByArgs` verifies requested CIDs and optionally removes bad blocks.

## Control Flow

List and verify handlers get the filestore, branch between explicit CID arguments and full scans, stream `filestore.ListRes` entries, and use CLI post-runs for formatted text with CID encoder support. `verify` optionally deletes bad blocks for statuses other than ok and other-error. `dups` iterates filestore keys and checks whether each also exists in the main blockstore, emitting refs.

## State and Persistence Behavior

`ls` and `dups` are read-only. `verify --remove-bad-blocks` mutates filestore metadata by deleting bad block links, with a warning that pinned data may be affected.

## Dependencies and Integration Points

Uses boxo filestore, Kubo node filestore/main blockstore, CID decoding, shared CID encoders, `refsEncoderMap`, and `streamResult`.

## Risks and Edge Cases

Filestore must be enabled or commands fail with `ErrFilestoreNotEnabled`. Removing bad blocks can affect pinned data and requires follow-up pin verification. Explicit invalid CIDs are emitted as per-entry errors rather than failing the whole command immediately.

## Test Signals

No direct tests. Useful tests include disabled filestore, explicit CID invalid/error statuses, full scan ordering, remove-bad-blocks action text, and duplicate detection errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/filestore.go -->
