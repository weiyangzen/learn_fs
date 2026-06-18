# sources/distributed-fs/ipfs-kubo/core/coreiface/unixfs.go

## Purpose
Defines CoreAPI UnixFS file/directory operations and listing event types.

## Important APIs, Types, and Functions
Declares `AddEvent`, `DirEntryType` constants `TUnknown`, `TFile`, `TDirectory`, `TSymlink`, `DirEntry`, and `UnixfsAPI` methods `Add`, `Get`, and `Ls`.

## Control Flow and State
There is no implementation flow. The interface describes importing files to content-addressed paths, retrieving paths as Boxo file nodes, and streaming directory entries through channels.

## Dependencies and Integration Points
Depends on context, Boxo files/path, CIDs, and UnixFS options. Implementations use `coreunix.Adder` and DAG/path resolvers.

## Risks and Test Signals
Risks include event channel ordering, directory entry close/error semantics, symlink targets, and random-access file support. Tests in `tests/unixfs.go` provide broad conformance coverage.
