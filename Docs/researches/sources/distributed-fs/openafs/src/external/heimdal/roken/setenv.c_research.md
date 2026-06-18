# sources/distributed-fs/openafs/src/external/heimdal/roken/setenv.c

## Purpose
Provides a fallback `setenv` implementation for platforms lacking it or needing a roken-compatible prototype.

## Important APIs, Types, And Functions
The exported function is `setenv(const char *var, const char *val, int rewrite)`, mapped to `rk_setenv` by `roken.h` when needed. Unix builds use `asprintf` and `putenv`; Windows builds use `GetEnvironmentVariable` and `SetEnvironmentVariable`.

## Control Flow
If `rewrite` is false and the variable already exists, it returns success without changing state. Unix builds allocate a `NAME=value` string and pass it to `putenv`, intentionally leaking the string because many `putenv` implementations keep the pointer. Windows builds call `SetEnvironmentVariable` directly.

## State And Persistence
The process environment is modified. Unix fallback allocations can persist until process exit.

## Dependencies And Integration Points
The function depends on roken formatting helpers, libc environment APIs, or Win32 environment APIs. It is declared by `roken.h.in` and used by portability code that wants BSD/POSIX `setenv` semantics.

## Risks And Test Signals
Unix memory retention is intentional but can matter for repeated changes in long-running processes. The implementation does not validate invalid names containing `=`. Tests should cover rewrite/no-rewrite, empty value, missing variable, Windows behavior, and interaction with subsequent `getenv` and `unsetenv`.
