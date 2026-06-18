# sources/distributed-fs/openafs/src/afs/FBSD/opt_posix.h

## Purpose
Defines FreeBSD POSIX option macros needed by OpenAFS kernel compilation.

## Important APIs, Types, And Functions
The file defines `P1003_1B` and `_KPOSIX_PRIORITY_SCHEDULING` to `1`.

## Control Flow
There is no runtime flow.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
Included by FreeBSD kernel code expecting POSIX scheduling feature macros.

## Risks
Hard-coded feature macros may not match all target FreeBSD kernels, but they preserve compatibility with code that conditionally compiles POSIX scheduling support.

## Test Signals
Successful FreeBSD builds are the signal.
