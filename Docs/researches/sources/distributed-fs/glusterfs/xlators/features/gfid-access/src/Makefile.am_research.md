# sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/Makefile.am

## Purpose
Builds the `gfid-access.la` feature translator.

## Important APIs, types, and functions
Defines source `gfid-access.c`, headers `gfid-access.h` and `gfid-access-mem-types.h`, installs under the feature xlator directory, and links against `libglusterfs`.

## Control flow
Automake compiles the translator with GlusterFS lib and RPC/XDR includes.

## State and persistence behavior
Build output is `gfid-access.so`; no runtime state in this Makefile.

## Dependencies and integration points
Part of GlusterFS xlator module build. The memory type header in this work item supports allocations in the implementation not listed here.

## Risks and test signals
Build risk is minimal; test by compiling the module and verifying install/uninstall paths.
