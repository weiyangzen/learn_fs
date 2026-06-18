# sources/distributed-fs/glusterfs/xlators/features/gfid-access/Makefile.am

## Purpose
Top-level Automake file for the gfid-access feature translator directory.

## Important APIs, types, and functions
Only `SUBDIRS = src`.

## Control flow
Recursive make enters `src`.

## State and persistence behavior
No direct state.

## Dependencies and integration points
Integrates gfid-access into the GlusterFS feature translator build.

## Risks and test signals
Low risk; verify recursive build enters `gfid-access/src`.
