# sources/distributed-fs/openafs/src/external/heimdal/roken/unsetenv.c

## Purpose
Provides a fallback `unsetenv` for platforms missing it.

## Important APIs, Types, And Functions
The exported function is `unsetenv(const char *name)`, declared as `rk_unsetenv` by `roken.h` when needed. It operates on the global `environ` array.

## Control Flow
The function rejects `NULL` names or missing `environ`, computes the variable-name length up to `=` or NUL, finds the first matching `NAME=` entry, and shifts all subsequent environment pointers left by one position.

## State And Persistence
The process environment vector is modified in place. The removed environment string is not freed, which matches the uncertainty around ownership of environment storage.

## Dependencies And Integration Points
Works with `setenv.c` and other roken environment helpers. Feature detection determines whether consumers call this implementation.

## Risks And Test Signals
Only the first matching entry is removed; duplicate environment variables can remain. Empty names are not explicitly rejected. Tests should cover existing/missing variables, names containing `=`, duplicates, empty names, and interaction with `setenv`.
