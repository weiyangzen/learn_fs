<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mfs/mfs_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mfs/mfs_unix.go

## Purpose

`mfs_unix.go` constructs the FUSE root for Kubo's mutable file system. It adapts `ipfs.FilesRoot.GetDirectory()` into the shared writable FUSE directory implementation.

## Important APIs, Types, and Functions

`NewFileSystem` returns `writable.NewDir` with `StoreMtime`, `StoreMode`, DAG service, repo path, and preferred block size derived from `Import.UnixFSChunker`.

## Control Flow, State, and Integration

There is no mount lifecycle here; it only builds the root object. Persistent state is Kubo's MFS DAG and repo datastore. The `RepoPath` flows into statfs, and `Blksize` flows into stat fields for tools such as `cp`, `du`, and `rsync`.

## Dependencies, Risks, and Test Signals

Dependencies are config, core, `fuse/mount`, and `fuse/writable`. The major risk is constructing writable roots without a DAG or with stale chunker-derived block size; `writable.NewDir` panics on missing DAG and tests cover block size normalization/stat behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mfs/mfs_unix.go -->
