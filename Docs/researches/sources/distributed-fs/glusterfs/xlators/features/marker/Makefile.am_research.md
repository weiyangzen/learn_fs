# sources/distributed-fs/glusterfs/xlators/features/marker/Makefile.am

## Purpose
This top-level automake file for the marker feature translator delegates all build work to the `src` subdirectory.

## Important APIs, Types, And Functions
There are no C APIs. The only meaningful variables are `SUBDIRS = src` and `CLEANFILES =`.

## Control Flow
Automake descends into `src`, where the actual `marker.la` translator target is declared. Cleanup has no extra files at this level.

## State, Dependencies, And Integration Points
The file participates in the GlusterFS autotools build. Its integration point is directory recursion; missing `src` would make the marker translator unavailable to the build.

## Risks And Test Signals
Risk is low. Build-system tests should confirm `make` enters `xlators/features/marker/src` and that dist/clean targets still work.
