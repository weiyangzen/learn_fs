# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/unixfs.go

## Purpose
Large CoreAPI conformance suite for UnixFS add, get, list, seek, read-at, pinning, hash-only, no-copy, events, progress, and close behavior.

## Important APIs, Types, and Functions
Defines fixtures `hello`, `emptyFile`, helpers `strFile`, `twoLevelDir`, `flatDir`, `wrapped`, close-test types, and tests `TestAdd`, `TestAddPinned`, `TestAddHashOnly`, `TestGetEmptyFile`, `TestGetDir`, `TestGetNonUnixfs`, `TestLs`, `TestEntriesExpired`, `TestLsEmptyDir`, `TestLsNonUnixfs`, `TestAddCloses`, `TestGetSeek`, and `TestGetReadAt`.

## Control Flow and State
`TestAdd` table-drives content through UnixFS add with CIDv1/raw leaves, alternate hash, inline, chunker/layout, offline, hash-only, directories/wrapping, hidden files, no-copy, events, silent, and progress options, then compares exact paths and round-trips content via `Get`. Later tests verify pin creation, hash-only non-storage, empty file read, directory retrieval, non-UnixFS errors, listing symlinks/files, canceled directory iterators, empty/non-UnixFS listing, input node closure, seek, and optional `ReaderAt`.

## Dependencies and Integration Points
Depends on Unixfs, Block, Pin, Dag APIs, options, Boxo files, UnixFS importer helpers, dag-cbor, CIDs, multihash, and random data.

## Risks and Test Signals
This is the main regression signal for UnixFS behavior: CID stability, option normalization, event ordering, no-copy path requirements, hash-only persistence, file closure, iterator cancellation, and random-access reads. It is large and exact-CID-heavy, so upstream UnixFS encoding changes require deliberate test updates.
