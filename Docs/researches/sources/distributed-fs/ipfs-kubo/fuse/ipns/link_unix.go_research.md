<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/link_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/ipns/link_unix.go

## Purpose

This file implements symlink nodes used by the `/ipns` FUSE root. They represent aliases such as `/ipns/local` and resolved remote IPNS names that point into `/ipfs`.

## Important APIs, Types, and Functions

`Link` embeds `fs.Inode` and stores a `Target`. `Getattr` sets symlink permissions, and `Readlink` returns the target bytes.

## Control Flow, State, and Integration

The object is immutable after construction by `Root.Lookup` or `CreateRoot`. It has no persistence of its own; it reflects root-level alias maps or resolved names. It integrates with go-fuse `NodeGetattrer` and `NodeReadlinker` behavior through method names.

## Dependencies, Risks, and Test Signals

Dependencies are go-fuse and syscall mode constants. The main risk is incomplete symlink attributes; mode here is permission bits, while stable inode type is supplied by the parent lookup. IPNS tests verify `/ipns/local` readlink behavior and readdir mode reporting through root entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/link_unix.go -->
