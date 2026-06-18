# sources/distributed-fs/openafs/src/platform/DFBSD/Makefile.in

## Purpose
Provides the DragonFly BSD platform directory makefile placeholder. It declares that this platform has no platform-specific userland support objects in this subtree.

## Important APIs, Types, And Functions
The only targets are `all`, `install`, `dest`, and `clean`, each intentionally empty. `SHELL=/bin/sh` is set for consistency with other platform makefiles.

## Control Flow
When the top-level platform dispatcher enters this directory, all build/install/clean phases complete immediately without producing artifacts.

## State And Persistence
No build outputs, installed files, or generated state are created.

## Dependencies And Integration Points
This file is reached through `src/platform/Makefile.in` via `$(MKAFS_OSTYPE)`. Its presence keeps the platform dispatch stable even though DragonFly BSD has no specific code here.

## Risks And Test Signals
The main risk is false confidence: a successful target means only that no platform support is required here. Test signal is that DragonFly BSD platform builds do not fail due to a missing directory or makefile.
