# sources/distributed-fs/coda/coda-src/librepair/cure.h

## Purpose
Header exposing directory conflict repair-plan helpers from `cure.cc`.

## APIs, Types, and Functions
Includes `vcrcommon.h` and declares `ObjExists()`, `RepairRename()`, `RepairSubsetCreate()`, and `RepairSubsetRemove()` over `resreplica`, `resdir_entry`, `listhdr`, `VolumeId`, vnode id, and unique id inputs.

## Control Flow, State, and Persistence
No runtime flow. The declared functions append operations to repair-list state that is later serialized into fix files or applied through Venus repair.

## Dependencies and Integration
Requires repair/resolution type declarations from included or previously included headers. Used by resolution code to invoke cure logic.

## Risks and Test Signals
Risks include missing include guards and depending on external declarations for several types. Test signals are compile-time inclusion from resolver modules and matching signatures with `cure.cc`.
