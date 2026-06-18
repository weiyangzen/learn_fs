# sources/distributed-fs/glusterfs/xlators/features/shard/Makefile.am

## Purpose
This top-level Automake fragment delegates the shard translator feature directory to `src`.

## Important APIs and control flow
`SUBDIRS = src` causes recursive builds to enter `xlators/features/shard/src`. `CLEANFILES =` is empty and contributes no local cleanup.

## State, dependencies, and integration
There is no runtime state. The file integrates the shard feature into the larger GlusterFS build traversal.

## Risks and test signals
If the `src` directory is not traversed, the shard translator will not be built. Build verification should check recursive Automake output includes `features/shard/src`.
