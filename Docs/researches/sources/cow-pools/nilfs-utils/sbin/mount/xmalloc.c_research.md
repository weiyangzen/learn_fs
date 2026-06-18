# File Research: sources/cow-pools/nilfs-utils/sbin/mount/xmalloc.c

## Scope

Fatal allocation helpers for legacy mount code.

## APIs And Behavior

- Global `at_die` hook can run cleanup before fatal exit.
- `die()` prints a formatted message, runs `at_die` if set, and exits with the supplied code.
- `xmalloc()` allocates nonzero sizes and dies on failure.
- `xrealloc()` reallocates and dies on failure.
- `xstrdup()` duplicates non-NULL strings and dies on failure; NULL input returns NULL.

## State And Dependencies

Uses NLS for the out-of-memory message and `EX_SYSERR` from `sundries.h`.

## Risks And Invariants

These helpers terminate the process rather than returning errors. `xmalloc(0)` returns NULL by design, so callers must not assume non-NULL for zero-byte allocations.
