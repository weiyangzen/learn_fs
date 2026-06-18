# sources/distributed-fs/beegfs/common/source/common/storage/Storagedata.h

## Purpose
Defines chunk storage on-disk layout constants.

## Important APIs, Types, And Functions
Exports chunk level fanout counts, chunk subdir name, user-ID prefix, and buddy-mirror chunk subdir name.

## Control Flow
No runtime logic.

## State, Persistence, And Dependencies
No state. Constants define persistent path layout.

## Integration Points
Used by storage server chunk path construction and buddy-mirrored chunk storage.

## Risks
Changing these constants breaks existing storage directory layouts.

## Test Signals
Path-construction tests and migration compatibility checks should cover them.
