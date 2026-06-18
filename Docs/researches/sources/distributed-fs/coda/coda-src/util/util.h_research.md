# sources/distributed-fs/coda/coda-src/util/util.h

## Purpose
Declares general Coda utility functions, logging macros, debug-level globals, and lock convenience macros.

## Important APIs, Types, And Functions
Public functions are `HashString`, `eprint`, `fdprint`, `LogMsg`, `PrintTimeStamp`, `UtilHostEq`, `hostname`, and `UtilDetach`. Macros include `TRUE`, `FALSE`, `VLog`, `SLog`, `DLog`, `ALog`, `CLog`, and `U_*lock` wrappers. Debug globals include server, volume, directory, ACL, and auth levels.

## Control Flow
Callers use package-specific logging macros, host utilities, and lock wrappers around LWP lock-bearing structures.

## State And Persistence
The header exposes process-global debug levels but no durable state.

## Dependencies And Integration Points
Includes `coda_assert`, POSIX/stdio/signal basics, and expects LWP lock functions for `U_*` macros. Used broadly by Coda sources.

## Risks
Macros depend on specific field names (`lock`) and global debug variables. Cygwin compatibility declarations may conflict with modern libc headers.

## Test Signals
Compile C/C++ users, check variadic macro support, lock macro use on structures with `lock`, and cross-platform builds.
