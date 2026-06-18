# sources/distributed-fs/openafs/src/afs/DFBSD/osi_inode.h

## Purpose
This file is an intentionally empty DragonFly BSD inode-compatibility header in this source snapshot.

## Important APIs, Types, And Functions
It declares no macros, types, or functions.

## Control Flow
There is no executable control flow.

## State And Persistence
No state is defined.

## Dependencies And Integration Points
Its presence satisfies include paths that expect a platform `osi_inode.h` for every BSD variant.

## Risks
Any code that expects DragonFly-specific inode macros from this header would fail to compile. The empty file implies either the platform does not support those inode operations or definitions come from elsewhere.

## Test Signals
DragonFly BSD builds are the primary signal. Include-only compilation should succeed for code paths that do not require inode metadata macros.
