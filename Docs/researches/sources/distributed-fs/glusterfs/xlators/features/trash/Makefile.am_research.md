# sources/distributed-fs/glusterfs/xlators/features/trash/Makefile.am

## Purpose
Top-level Automake file for the trash feature translator directory. It delegates all build work to `src`.

## Important APIs, Types, and Functions
- `SUBDIRS = src` makes Automake recurse into the implementation directory.
- `CLEANFILES =` is present but empty.

## Control Flow
Build-system only: configure/make recurses into `src/Makefile.am`.

## State and Persistence
No runtime state. Build output state is controlled by the child makefile.

## Dependencies and Integration Points
Integrated by the broader GlusterFS build tree. It depends on Automake recursion and the `src` directory existing.

## Risks
If recursion is removed, `trash.la` will not be built. Empty `CLEANFILES` is harmless but redundant.

## Test Signals
`make` or `make distcheck` should include `xlators/features/trash/src`.
