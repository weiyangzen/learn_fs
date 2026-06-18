# sources/distributed-fs/glusterfs/xlators/performance/io-threads/Makefile.am

## Purpose
Routes automake recursion for the io-threads translator into its `src` directory.

## Important APIs, types, and functions
`SUBDIRS = src` is the effective build rule. `CLEANFILES` is empty.

## Control flow
The parent performance build enters this directory, then recurses into `src` to build `io-threads.la`.

## State and persistence behavior
No runtime state exists; the file persists only build topology.

## Dependencies and integration points
Depends on `src/Makefile.am` and the parent `xlators/performance` automake setup.

## Risks and test signals
Risks are broken recursion or an unbuilt translator if the child directory is renamed. Build tests should confirm the io-threads module is produced and installed.
