# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/path.go

## Purpose
Conformance tests for path mutability, joins, root resolution, and unresolved remainder reporting.

## Important APIs, Types, and Functions
Defines `newIPLDPath` and tests `TestMutablePath`, `TestPathRemainder`, `TestEmptyPathRemainder`, `TestInvalidPathRemainder`, `TestPathRoot`, and `TestPathJoin`.

## Control Flow and State
Tests create raw blocks and dag-cbor nodes, resolve paths through `CoreAPI.ResolvePath`, assert mutable status for key paths versus block paths, compare unresolved remainder slices, verify invalid traversal errors, and validate `path.Join`.

## Dependencies and Integration Points
Depends on BlockAPI, DagAPI, KeyAPI, path utilities, dag-cbor, and UnixFS/IPLD path namespaces.

## Risks and Test Signals
Signals include correct root CID extraction after IPLD traversal and remainder behavior. It does not cover IPNS mutable resolution depth or UnixFS path traversal extensively.
