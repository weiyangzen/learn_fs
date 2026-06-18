<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/fs.go -->
# sources/cloud-native/stargz-snapshotter/store/fs.go

## Purpose
Implements the FUSE filesystem for stargz-store, exposing image references and layers as a virtual tree that can resolve lazy layers, expose layer contents, raw blobs, and metadata.

## Important APIs, Types, And Functions
- `Mount(ctx, mountpoint, layerManager, debug)` creates and mounts a go-fuse server.
- `rootnode.Lookup` exposes `pool` and base64-encoded image reference directories.
- `refnode.Lookup` exposes digest-named layer directories; `Rmdir` releases layer references.
- `layernode.Create` treats creating hidden `use` as a reference increment.
- `layernode.Lookup` serves `info`, `diff`, `blob`, and hidden `use` names.
- `blobfile.Read` reads raw layer bytes with direct cache and context cancellation.
- Attribute and inode helpers maintain stable permissions and unique IDs.

## Control Flow
Mount setup chooses `fusermount` with `suid` when available, otherwise direct mount. Lookups decode a ref, parse a digest, resolve layer info or data through `LayerManager`, verify target digest, and then either materialize memory files, raw blob file handles, or the layer root node. Reference accounting is driven by synthetic file creation and directory removal.

## State And Persistence
The FUSE tree is virtual, but it references persistent pool metadata under `refPool.root()` and layer caches managed by `LayerManager`. Inode IDs are in-memory and released on `OnForget`.

## Dependencies And Integration Points
Depends on go-fuse, containerd references, opencontainers digests, stargz layer interfaces, remote/cache options, and `LayerManager` for resolution/lifetime.

## Risks And Edge Cases
Clients must know to base64-encode image refs. `Rmdir` intentionally returns `ENOENT` after release signaling. Resolve failures are logged with remote preparation status. Inode ID allocation is linear and can become expensive at extreme counts.

## Test Signals
Useful tests would mount the store, resolve `pool`, base64 ref directories, `info` JSON, `diff` contents, `blob` reads, hidden `use` reference increments, and release cleanup through `Rmdir`.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/fs.go -->
