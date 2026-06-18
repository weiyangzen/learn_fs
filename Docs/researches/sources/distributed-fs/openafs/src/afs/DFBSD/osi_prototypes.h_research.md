# sources/distributed-fs/openafs/src/afs/DFBSD/osi_prototypes.h

## Purpose
Provides the DragonFly BSD platform prototypes include guard for OpenAFS.

## Important APIs, Types, And Functions
No routines are declared in this snapshot.

## Control Flow
There is no executable flow.

## State And Persistence
No state is defined.

## Dependencies And Integration Points
The header is an include boundary for platform-specific helpers, even though this platform currently exposes none here.

## Risks
Missing prototypes can hide implicit-declaration problems if DragonFly-specific support functions are later added without updating this header.

## Test Signals
Compiler warnings and full DragonFly builds are the useful signals.
