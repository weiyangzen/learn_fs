# sources/distributed-fs/glusterfs/xlators/performance/io-cache/Makefile.am

## Purpose
Routes automake recursion for the io-cache translator into its `src` directory.

## Important APIs, types, and functions
`SUBDIRS = src` is the only functional build contract. `CLEANFILES` is empty.

## Control flow
The performance parent makefile enters this directory, then automake enters `src`, where `io-cache.la` is built.

## State and persistence behavior
No runtime state exists; this file only persists the module's build topology.

## Dependencies and integration points
Depends on `src/Makefile.am` to define the actual shared xlator. It integrates with the parent performance translator build.

## Risks and test signals
The main risk is a broken recursive build if `src` is renamed or omitted. Build tests should confirm `io-cache.la` is produced from a clean tree.
