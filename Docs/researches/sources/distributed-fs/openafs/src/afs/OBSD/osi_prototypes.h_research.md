# sources/distributed-fs/openafs/src/afs/OBSD/osi_prototypes.h

## Purpose
Placeholder OpenBSD OSI prototypes header.

## Important APIs, Types, and Functions
Contains only an include guard and a stale comment saying "macos support routines"; it declares nothing.

## Control Flow
None.

## State and Persistence
None.

## Dependencies and Integration Points
Provides a platform header name expected by shared include paths without exporting OpenBSD-specific prototypes.

## Risks
The misleading comment and lack of prototypes can hide missing declarations until compile/link time.

## Test Signals
Build OpenBSD kernel module with warnings enabled for missing prototypes and verify consumers do not rely on declarations from this header.
