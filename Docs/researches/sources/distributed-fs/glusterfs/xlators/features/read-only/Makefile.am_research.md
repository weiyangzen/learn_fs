# sources/distributed-fs/glusterfs/xlators/features/read-only/Makefile.am

## Purpose
This top-level automake file declares the `read-only` feature subdirectory for recursive build traversal.

## Important APIs and Build Targets
- `SUBDIRS = src` delegates all implementation build work to `src/Makefile.am`.
- `CLEANFILES =` is present but empty.

## Control Flow
There is no runtime control flow. Build systems process this file to enter the `src` directory.

## State and Persistence
No runtime state or generated persistent data is defined here beyond normal build artifacts produced by the subdirectory.

## Dependencies and Integration Points
It integrates with the GlusterFS automake tree. The child `src` makefile defines the actual `read-only.la` and `worm.la` modules.

## Risks
If `SUBDIRS` is changed or removed, the read-only and WORM translators will not build. Empty `CLEANFILES` is harmless.

## Test Signals
Autotools configure/build should descend into `xlators/features/read-only/src` and produce both feature modules when enabled by the parent build.
