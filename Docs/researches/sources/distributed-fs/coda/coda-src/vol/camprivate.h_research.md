# sources/distributed-fs/coda/coda-src/vol/camprivate.h

## Purpose

`sources/distributed-fs/coda/coda-src/vol/camprivate.h` declares private Camelot/RVM storage layout structures for the Coda volume package.

## Important APIs, Types, and Functions

It defines `struct VolumeData`, containing a `VolumeDiskData *`, arrays/lists for small and large vnode lists, counts of allocated vnodes and vnode lists, and reserved fields. It also defines `struct VolHead`, combining a `VolumeHeader` with `VolumeData`.

## Control Flow

There is no executable flow. The structures are consumed by recovery/storage code to navigate top-level volume metadata in recoverable storage.

## State and Persistence Behavior

These structures describe persistent RVM/Camelot state. `VolumeData` points to volume disk metadata and recoverable vnode-list arrays. Reserved fields protect future layout growth if fields are inserted before the reserved tail and the reserved count is reduced.

## Dependencies and Integration Points

The header includes `rec_smolist.h` and depends on `VolumeDiskData`, `VolumeHeader`, `bit32`, and vnode-list types from the volume package. It is used by low-level recovery/index code rather than high-level RPC handlers.

## Risks and Edge Cases

Because this is a persistent layout contract, reordering or resizing fields can break existing recoverable storage. Pointer fields are meaningful inside the RVM segment and require correct recovery/remapping. Reserved capacity must be managed carefully during migrations.

## Test Signals

Run recovery initialization and salvage tests against existing RVM segments; add structure-size/layout checks for migration-sensitive builds; verify volume attach/detach and vnode-list traversal after restart.
