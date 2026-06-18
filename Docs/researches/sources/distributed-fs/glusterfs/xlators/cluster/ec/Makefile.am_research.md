# sources/distributed-fs/glusterfs/xlators/cluster/ec/Makefile.am

## Purpose
Top-level Automake file for the GlusterFS erasure-code/disperse cluster translator directory. It delegates the actual build to the `src` subdirectory and declares an empty cleanup variable.

## Important APIs and Functions
- `SUBDIRS = src`: tells Automake to recurse into `xlators/cluster/ec/src`.
- `CLEANFILES =`: placeholder for generated files to remove during cleanup.

## Control Flow
Automake processes this directory, then builds the implementation through `src/Makefile.am`. There is no runtime control flow.

## State and Persistence
No runtime state. Build state is limited to generated Makefile artifacts and recursive build traversal.

## Dependencies and Integration Points
Integrates with the repository Autotools build. The `src` subdirectory defines the actual `ec.la` xlator target and install hooks.

## Risks
Minimal. The file must keep `src` in `SUBDIRS`; removing it would omit the EC translator from recursive builds.

## Test Signals
Build-system signal is whether `make` descends into `xlators/cluster/ec/src` and produces the EC/disperse translator.
