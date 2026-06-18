# sources/distributed-fs/coda/coda-src/util/mkpath.h

## Purpose
Declares the recursive parent-directory creation helper.

## Important APIs, Types, And Functions
`int mkpath(const char *name, mode_t mode)` returns 0 on success and -1 with `errno` set on failure.

## Control Flow
Callers invoke it before creating a file to ensure the containing directory hierarchy exists.

## State And Persistence
The API affects filesystem directory state through the implementation.

## Dependencies And Integration Points
Requires `mode_t` to be visible from included system headers. Used by C and C++ code.

## Risks
The `const` qualifier does not match implementation behavior, which temporarily writes into `name`.

## Test Signals
Compile users with proper `mode_t` includes and test mutable path buffers.
