<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/readonly_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/readonly/readonly_unix.go

## Purpose

`readonly_unix.go` implements the read-only `/ipfs` FUSE filesystem. It maps immutable `/ipfs/<cid>/<path>` names to UnixFS DAG nodes and exposes files, directories, symlinks, stat fields, and CID xattrs.

## Important APIs, Types, and Functions

`Root` stores the node and repo path. `Root.Lookup` parses immutable paths, resolves with `UnixFSPathResolver`, decodes raw or dag-pb blocks, fills entry attrs, and returns `Node`. `Root.Statfs`, `Getattr`, and `Readdir` handle namespace behavior. `Node` wraps an IPLD node and lazily caches `unixfs.FSNode`. `Node.Open` returns a serialized `roFileHandle` with a DagReader. `fillAttr`, `Lookup`, `Readdir`, `Listxattr`, `Getxattr`, `Readlink`, `roFileHandle.Read`, `Release`, and `stableAttrFor` implement the FUSE contracts.

## Control Flow, State, and Integration

Lookups traverse immutable CIDs and child links, readdir fetches child nodes to infer file types, opens create per-handle DagReaders, and reads seek to the requested offset before context-aware reads. Kernel cache time is set to one year because `/ipfs` paths are content-addressed. Persistent state is only the underlying blockstore/DAG; this filesystem does not mutate it.

## Dependencies, Risks, and Test Signals

Dependencies include go-fuse, boxo UnixFS, merkledag, DAG reader, Kubo core resolvers/blockstore, CID links, and shared mount helpers. Risks include unsupported codecs, not-found handling, non-thread-safe DagReader access, stale attr fill causing zero-mode cache, expensive readdir child fetches, and large immutable cache for malformed names. The readonly test file covers raw leaves, symlinks, xattrs, stat fields, concurrent reads, and cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/readonly_unix.go -->
