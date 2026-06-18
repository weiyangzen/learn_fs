# sources/distributed-fs/openafs/src/platform/OBSD/Makefile.in

## Purpose
Provides an empty OpenBSD platform-specific makefile.

## Important APIs, Types, And Functions
Defines standard no-op `all`, `install`, `dest`, and `clean` targets.

## Control Flow
The common platform makefile can delegate into `OBSD` for any standard phase without doing work.

## State And Persistence
No artifacts are generated, installed, or removed.

## Dependencies And Integration Points
Serves the OpenBSD branch of `$(MKAFS_OSTYPE)` platform dispatch.

## Risks And Test Signals
Risk is only missing target updates if this directory gains real code. Test signal is successful OpenBSD build traversal.
