# sources/distributed-fs/glusterfs/xlators/performance/write-behind/Makefile.am

## Purpose
Top-level Automake file for the `performance/write-behind` translator directory.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src` and empty `CLEANFILES`.

## Control Flow
The build system descends into `src` to compile the actual module.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Integrated by parent performance translator build files.

## Risks
If `src` is not listed, write-behind will not be built or installed.

## Test Signals
Parent builds should enter `write-behind/src` and produce the xlator module.
