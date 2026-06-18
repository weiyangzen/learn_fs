# sources/distributed-fs/glusterfs/xlators/features/upcall/Makefile.am

## Purpose
Top-level Automake file for the upcall feature translator directory.

## Important APIs, Types, and Functions
- `SUBDIRS = src` recurses into implementation.
- `CLEANFILES =` is empty.

## Control Flow
Build-system recursion only.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrated by parent GlusterFS Automake tree.

## Risks
Removing `src` recursion would omit the upcall translator.

## Test Signals
`make` should descend into `xlators/features/upcall/src`.
