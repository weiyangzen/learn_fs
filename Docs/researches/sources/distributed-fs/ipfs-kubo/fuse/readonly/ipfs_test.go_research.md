<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/ipfs_test.go -->
# sources/distributed-fs/ipfs-kubo/fuse/readonly/ipfs_test.go

## Purpose

This file tests the read-only `/ipfs` FUSE implementation directly, covering CID lookup, UnixFS directory traversal, raw leaves, metadata, symlinks, xattrs, stat fields, read cancellation, and concurrency.

## Important APIs, Types, and Functions

`testMount` mounts readonly roots with immutable cache settings. `randObj` builds random trickle DAGs. `setupIpfsTest` creates a mock node and mounts `NewRoot`. Tests cover empty directories, bare CIDv0/CIDv1 reads, mixed dag-pb/raw directories, basic file and directory reads, stress reads, file size reporting, UnixFS metadata, default modes, CID xattrs, symlink readlink/readdir, seek reads, concurrent large-file reads, cancellation through `blockingDagReader`, stat blocks, statfs, and unknown xattrs.

## Control Flow, State, and Integration

Tests construct DAG nodes in a mock node's blockstore, then access them through normal filesystem operations under the FUSE mount. The cancellation test bypasses mounting and directly invokes `roFileHandle.Read` with a fake blocking reader.

## Dependencies, Risks, and Test Signals

Dependencies include coremock, CoreAPI, boxo UnixFS importer/io, go-fuse, and fusetest. The tests guard high-risk areas: raw leaf decoding, stable inode types, kernel attr caching, concurrent readahead against non-thread-safe DagReaders, cancellation-to-EINTR mapping, and POSIX stat/xattr behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/ipfs_test.go -->
