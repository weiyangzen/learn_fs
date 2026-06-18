# sources/distributed-fs/openafs/src/platform/NBSD/Makefile.in

## Purpose
Provides an empty NetBSD platform-specific makefile so platform dispatch has standard targets.

## Important APIs, Types, And Functions
Exposes no-op `all`, `install`, `dest`, and `clean` targets.

## Control Flow
All standard target invocations complete without invoking compilers or installers.

## State And Persistence
No persistent state or build output is created.

## Dependencies And Integration Points
Selected by the common platform dispatcher for NetBSD builds.

## Risks And Test Signals
Risk is future platform work not wired into these targets. Test signal is successful no-op dispatch.
