# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/ListStatusPartial.java

## Purpose
`ListStatusPartial` contains helper logic for paginated and prefix-filtered `listStatus` traversal. It validates offsets, converts `startAfter` and offset ids into path-component cursors, checks prefix compatibility, and selects inode-store child iterators that start at the correct point.

## Important APIs, types, and functions
Static helpers include `checkPartialListingOffset`, `computePartialListingPaths`, `checkPrefixListingPaths`, `getChildrenIterator`, and `hasPrefixComponentsCanBeLonger`. They operate on `ListStatusContext`, `ListStatusPartialPOptions`, `InodeTree`, `LockedInodePath`, `ReadOnlyInodeStore`, and path component lists.

## Control flow
Offset validation resolves the offset inode id back to component names and confirms it is under the requested listing path. Initial listings can use `startAfter`; absolute `startAfter` values are checked against the listing root before being converted to relative components. Prefix options are split into components and validated against non-initial partial cursors. Child iterator selection chooses among full child listing, prefix listing, listing from a cursor, or prefix-from-cursor listing based on options and traversal depth.

## State and persistence behavior
The class is stateless and does not mutate master state. It influences what metadata is read and how many results are returned by the surrounding listing implementation.

## Dependencies and integration points
It depends on inode tree path lookup, read-only inode-store child iterators, Alluxio path utilities, partial listing protobuf options, and `ListStatusContext` counters/truncation logic elsewhere. It is used by `DefaultFileSystemMaster` list traversal for partial listings.

## Risks
Cursor validation is subtle: offset ids can be stale, renamed, or outside the requested subtree. Prefix semantics intentionally allow the prefix to be longer than the cursor components if prior components match. Absolute and relative `startAfter` normalization must remain consistent with client expectations. Iterator choice assumes inode-store ordering by name.

## Test signals
`FileSystemMasterPartialListingTest` is the primary signal, with cases for offsets, `startAfter`, prefix filters, invalid offsets, truncation, nested directories, and missing paths. Unit tests for `hasPrefixComponentsCanBeLonger` and iterator selection help isolate edge cases.
