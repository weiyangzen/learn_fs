# sources/distributed-fs/ceph-client/drivers/staging/most/Makefile

## Purpose
Routes enabled MOST component builds into their subdirectories.

## Important APIs, Types, And Functions
Adds `net/`, `video/`, and `dim2/` directories based on `CONFIG_MOST_NET`, `CONFIG_MOST_VIDEO`, and `CONFIG_MOST_DIM2`.

## Control Flow
Build-time only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Works with child Kconfig symbols and subdirectory Makefiles.

## Risks And Test Signals
Incorrect object routing would omit selected modules. Test signal is an allmodconfig or targeted staging MOST build.
