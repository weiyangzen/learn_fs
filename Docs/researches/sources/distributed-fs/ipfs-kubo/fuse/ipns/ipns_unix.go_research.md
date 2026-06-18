<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/ipns_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/ipns/ipns_unix.go

## Purpose

`ipns_unix.go` implements the FUSE tree for `/ipns` on supported platforms. Local keys are writable directories backed by MFS roots, aliases are symlinks to key IDs, and non-local IPNS names resolve to read-only symlinks into the `/ipfs` mount.

## Important APIs, Types, and Functions

`Root` stores CoreAPI, key aliases, local writable directories, MFS roots, symlinks, mount roots, and repo path. `ipnsPubFunc` publishes updated MFS root CIDs with `Name().Publish`, marking the context via `fusemount.ContextWithPublish`. `loadRoot` resolves the key path or falls back to an empty directory, builds an `mfs.Root`, and wraps it in `writable.NewDir`. `CreateRoot` builds writable config from mount/import settings and creates all local key directories and alias links. `Root` implements `Getattr`, `Statfs`, `Lookup`, `Readdir`, and `Close`.

## Control Flow, State, and Integration

Lookup first hides macOS probe names, then returns local alias symlinks, local writable directories, or resolves arbitrary `/ipns/<name>` and maps IPFS results to `/ipfs/<cid>` symlinks. `Close` closes all MFS roots, which flushes and publishes local key state. State persists through the MFS root DAG, pinning/datastore, and IPNS records.

## Dependencies, Risks, and Test Signals

Dependencies include CoreAPI, namesys, mfs, UnixFS DAG services, config, `fuse/writable`, and `internal/fusemount`. High-risk behavior includes local publishes being blocked without the context bypass, non-protobuf IPNS roots, stale kernel cache for mutable entries, and external publishes overwriting local mount state. Tests check local alias links, persistence across unmount/remount, statfs, and the shared writable suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/ipns_unix.go -->
