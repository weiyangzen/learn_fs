# sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/Makefile.am

## Purpose
Top-level Automake file for the `performance/readdir-ahead` translator directory.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src` and an empty `CLEANFILES`.

## Control Flow
Automake descends into `src`, where the actual module build is defined.

## State And Persistence
No runtime state. It affects source-tree build traversal only.

## Dependencies And Integration Points
Integrated by the parent performance translator Makefile and GlusterFS build system.

## Risks
If `src` is omitted or renamed here, the translator library will not be built. No install artifacts are declared at this level.

## Test Signals
`make` from the parent should enter `readdir-ahead/src` and build `readdir-ahead.la`.
