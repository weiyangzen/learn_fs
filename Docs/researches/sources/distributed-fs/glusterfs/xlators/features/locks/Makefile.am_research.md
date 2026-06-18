# sources/distributed-fs/glusterfs/xlators/features/locks/Makefile.am

## Purpose
Top-level Automake file for the locks feature translator.

## Important APIs, Types, and Functions
No C APIs are defined. `SUBDIRS = src` delegates build work to the source directory.

## Control Flow
Automake descends into `src`.

## State and Persistence
No runtime state. `CLEANFILES` is empty.

## Dependencies and Integration Points
Part of the GlusterFS recursive build.

## Risks and Edge Cases
If `src` is omitted, the locks translator and clear-lock helper would not build.

## Test Signals
Server builds should enter the source directory and build `locks.la`.
