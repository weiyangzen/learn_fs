# sources/distributed-fs/glusterfs/xlators/features/leases/Makefile.am

## Purpose
Top-level Automake file for the leases feature translator.

## Important APIs, Types, and Functions
No C APIs are defined. `SUBDIRS = src` delegates to the source build file.

## Control Flow
Automake descends into `src`.

## State and Persistence
No runtime state. `CLEANFILES` is empty.

## Dependencies and Integration Points
Part of the GlusterFS recursive build.

## Risks and Edge Cases
Removing `src` from `SUBDIRS` would omit the leases translator from builds.

## Test Signals
Server build should visit this directory and build `leases.la` through the child Makefile.
