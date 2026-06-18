# sources/distributed-fs/ipfs-kubo/client/rpc/apifile.go

## Purpose
This file adapts remote UnixFS paths returned by the HTTP API into Boxo `files.Node`, `files.File`, `files.Directory`, and symlink abstractions.

## Important APIs, Types, And Functions
`UnixfsAPI.Get` resolves mutable paths, calls `files/stat`, parses mode/mtime/type, and dispatches to `getFile`, `getDir`, or `getSymlink`. `apiFile` supports `Read`, `ReadAt`, `Seek`, `Close`, `Mode`, `ModTime`, and `Size`. `apiDir` returns an `apiIter` over streaming `ls` output.

## Control Flow
Files are read through `cat`, with small forward seeks optimized by discarding from the existing stream and random reads done with offset/length requests. Directories issue streaming `ls`, buffer the response, and lazily build child nodes from each decoded link. Symlinks read target content via `cat`.

## State And Persistence Behavior
State is client-side stream position, open HTTP response, stat metadata, and buffered directory listing. Remote block/repo state is read-only.

## Dependencies And Integration Points
It integrates `files/stat`, `cat`, `ls`, Boxo UnixFS type constants, path resolution, and JSON streaming.

## Risks And Test Signals
Risks include directory buffering despite stream mode, response leak on early error, seek behavior on closed streams, and unsupported UnixFS types. Signals come from RPC CoreAPI UnixFS tests exercising reads, seeks, directories, symlinks, sizes, modes, and mtimes.
