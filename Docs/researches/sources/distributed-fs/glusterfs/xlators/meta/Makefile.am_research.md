# sources/distributed-fs/glusterfs/xlators/meta/Makefile.am

## Purpose
Top-level Automake recursion file for the meta translator.

## Important APIs, Types, and Functions
- `SUBDIRS = src`.

## Control Flow
Build recursion only.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrated by GlusterFS xlator build tree.

## Risks
Removing recursion prevents `meta.la` from building.

## Test Signals
`make` should descend into `xlators/meta/src`.
