# sources/distributed-fs/coda/coda-src/util/vice_file.h

## Purpose
Declares helpers for configuring and constructing paths under the Coda server vice directory.

## Important APIs, Types, And Functions
`vice_dir_init(const char *)` sets the root. `vice_config_path(const char *)` returns the root path or root plus a relative name.

## Control Flow
Programs initialize once from config, then use `vice_config_path()` for all vice-tree file lookups.

## State And Persistence
The API hides static process-global path state and does not modify disk state.

## Dependencies And Integration Points
C/C++ compatible header used by Coda server components.

## Risks
The returned pointer lifetime and static-buffer reuse are not visible from the signature.

## Test Signals
Compile C and C++ callers, verify initialization before use, and validate returned paths for null and non-null names.
