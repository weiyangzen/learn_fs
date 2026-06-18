# sources/distributed-fs/glusterfs/xlators/features/sdfs/Makefile.am

## Purpose
This top-level automake file declares the SDFS feature subdirectory for recursive build traversal.

## Important APIs and Build Targets
- `SUBDIRS = src` delegates build work to the implementation directory.
- `CLEANFILES =` is present but empty.

## Control Flow
No runtime control flow. Automake uses this file to descend into `src`.

## State and Persistence
No runtime state or persistent data is defined here.

## Dependencies and Integration Points
It integrates with the GlusterFS build tree and the child `src/Makefile.am`, which conditionally builds `sdfs.la`.

## Risks
If the subdirectory is removed from traversal, SDFS sources and message headers will not build or install.

## Test Signals
Autotools build should enter `xlators/features/sdfs/src`; build logs are the main signal.
