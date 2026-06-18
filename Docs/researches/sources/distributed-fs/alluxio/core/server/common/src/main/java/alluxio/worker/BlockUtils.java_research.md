# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/worker/BlockUtils.java

## Purpose
`BlockUtils` contains worker-side block helper methods. In this file it computes the UFS fallback path for a block.

## Important APIs, Types, and Functions
It defines `getUfsBlockPath(UfsManager.UfsClient, long)` and a private magic number `0x1D91AC0E01AB0165L`.

## Control Flow, State, and Persistence
The method concatenates the UFS mount point URI, a deterministic temporary directory name generated from the magic number and suffix `.alluxio_ufs_blocks`, and the block id. It does not touch storage directly.

## Dependencies and Integration Points
It depends on `UfsManager.UfsClient` and `PathUtils`. Worker block storage fallback code uses this path convention when writing blocks to UFS.

## Risks and Test Signals
Risks include path convention compatibility, mount URI formatting, and collisions if the magic/suffix changes. Signals are deterministic paths for known mount/block ids and compatibility with UFS cleanup/listing code.
