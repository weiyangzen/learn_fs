# sources/distributed-fs/glusterfs/xlators/performance/md-cache/Makefile.am

## Purpose
Routes automake recursion for the md-cache translator into its `src` directory.

## Important APIs, types, and functions
`SUBDIRS = src` is the only functional build declaration.

## Control flow
The parent performance build enters this directory, then enters `src` to build and install `md-cache.la`.

## State and persistence behavior
No runtime state exists; this is build metadata.

## Dependencies and integration points
Depends on the child `src/Makefile.am` and parent performance automake recursion.

## Risks and test signals
Risks are failing to build/install md-cache if recursion is broken. Build and install tests should confirm `md-cache.so` is produced.
