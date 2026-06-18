# sources/distributed-fs/coda/coda-src/vol/clone.cc

## Purpose

`sources/distributed-fs/coda/coda-src/vol/clone.cc` implements volume cloning for the Coda volume package. It copies large and small vnode indexes from an original volume to a new clone, updates inode reference counts, marks writable original directories as cloned for copy-on-write, and removes an older backup clone if supplied.

## Important APIs, Types, and Functions

Public API: `CloneVolume(Error *error, Volume *original, Volume *newv, Volume *old)`. Private helpers: `CloneIndex(Volume *ovp, Volume *cvp, Volume *dvp, VnodeClass vclass)` and `FinalDelete(Volume *vp)`.

## Control Flow

`CloneVolume` initializes the error, clones both `vLarge` and `vSmall` indexes, copies the original volume header to the new volume, and finally deletes/detaches the old backup. `CloneIndex` iterates the original index, optionally reads the corresponding old-backup vnode at the same offset, increments inode refs for containers shared with the new clone, decrements inode refs no longer referenced by the old backup, marks writable original directory vnodes cloned and bumps their data version before writing them back, then writes the vnode image into the clone index. A second pass over the old backup decrements remaining vnode inodes.

## State and Persistence Behavior

The file mutates vnode indexes and inode reference counts on disk/RVM. Writable original directories get `cloned = 1` and `dataVersion++` so later copy-on-write creates newer directory containers and salvage can reason about data versions. The clone receives a clean copy with the clone flag cleared and data version restored. `FinalDelete` removes the old backup volume metadata and detaches the volume object.

## Dependencies and Integration Points

It depends on `vindex`, `vindex_iterator`, `VnodeClassInfo`, `VolumeWriteable`, `CopyVolumeHeader`, inode refcount APIs (`iinc`, `idec`), `DeleteVolume`, `VDetachVolume`, volume/vnode structures, and partition/device ids. It integrates with later `CopyOnWrite` logic in server mutation paths.

## Risks and Edge Cases

The code assumes same-offset correspondence between original and old backup indexes and asserts heavily on inode and index operations. It reads `VnodeClassInfo[vclass]`, while nearby code uses `VnodeClassInfo_Array`, so build-time symbol compatibility matters. Directory clone data-version handling is subtle and explicitly called important for salvage. The second old-backup pass can double-decrement if index correspondence assumptions are wrong.

## Test Signals

Test cloning writable and readonly volumes, cloning with and without an old backup, directory copy-on-write after clone, inode reference counts before and after clone deletion, salvage after interrupted clone/COW, and both small and large vnode classes.
