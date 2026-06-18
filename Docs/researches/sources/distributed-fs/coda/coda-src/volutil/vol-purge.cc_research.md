# sources/distributed-fs/coda/coda-src/volutil/vol-purge.cc

## Purpose

`vol-purge.cc` implements `S_VolPurge`, the destructive administrative RPC that removes a named volume from recoverable and in-memory volume state. The complete 171-line file was read.

## Important APIs, Types, and Functions

The service entry point is `S_VolPurge(RPC2_Handle, RPC2_Unsigned, RPC2_String)`. It uses `VInitVolUtil()`, `VGetVolume()`, `VAttachVolume()`, `VOffline()`, `DeleteVolume()`, `VDisconnectFS()`, and the LWP `FSTAG` `ProgramType` rock to temporarily act as a fileserver for offline transition.

## Control Flow

The handler initializes volume utility mode, gets or attaches the target volume, verifies the caller-supplied name matches the internal volume name, forces the volume offline if it was online, asserts it is no longer in use, deletes the volume, marks the VM object as shutting down, prints the hash table, disconnects from the fileserver, and returns either the purge status or earlier error.

## State and Persistence Behavior

`DeleteVolume()` removes volume state from RVM and VM structures and should handle inode/header cleanup through the volume layer. The handler does not start its own RVM transaction; it relies on lower-level delete semantics. It mutates the per-LWP program type while forcing `VOffline()`.

## Dependencies and Integration Points

Dependencies include `rvmlib`, `volume.h`, `viceinode.h`, `partition.h`, `vutil.h`, `recov.h`, and `volutil.h`. It is called by the `volutil purge VolumeId VolumeName` client path and interacts with normal volume attachment/offline machinery.

## Risks and Test Signals

Risks include destructive action guarded only by id plus exact name, reliance on asserts for offline/in-use invariants, no callback to put an unexpectedly attached volume back online on late failure, and ambiguous handling of offline `VGetVolume()` results. Tests should cover online purge, already-offline purge, name mismatch, nonexistent volume, attach failure, and post-purge hash/RVM absence.
