# sources/distributed-fs/glusterfs/xlators/features/index/Makefile.am

## Purpose
Top-level Automake file for the index feature translator directory.

## Important APIs, Types, and Functions
No C APIs are defined. `SUBDIRS = src` delegates all build logic to the source subdirectory.

## Control Flow
Automake descends into `src` when building this component.

## State and Persistence
No runtime state. `CLEANFILES` is empty.

## Dependencies and Integration Points
Participates in the GlusterFS recursive build and relies on the `src/Makefile.am` for actual library targets.

## Risks and Edge Cases
Risk is limited to build-system omission; if `src` is removed from `SUBDIRS`, the index translator would not build.

## Test Signals
`make` or `make distcheck` should include the `src` target and produce `index.la` when server builds are enabled.
