# sources/distributed-fs/glusterfs/xlators/features/utime/Makefile.am

## Purpose
Top-level Automake recursion file for the utime feature translator.

## Important APIs, Types, and Functions
- `SUBDIRS = src`.
- Empty `CLEANFILES`.

## Control Flow
Build recursion into `src`.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrated by GlusterFS feature translator build tree.

## Risks
Without this recursion, `utime.la` and generated fops are omitted.

## Test Signals
`make` should descend into utime `src`.
