# sources/distributed-fs/glusterfs/xlators/features/compress/Makefile.am

## Purpose
Top-level Automake file for the compress/CDD feature translator directory.

## Important APIs, types, and functions
Only `SUBDIRS = src` and empty `CLEANFILES`.

## Control flow
Recursive make descends to `src`.

## State and persistence behavior
No direct runtime state.

## Dependencies and integration points
Integrates the compression translator subtree into the GlusterFS build.

## Risks and test signals
Low risk; verify recursive build reaches `compress/src`.
