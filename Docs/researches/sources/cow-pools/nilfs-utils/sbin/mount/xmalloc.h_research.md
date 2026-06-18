# File Research: sources/cow-pools/nilfs-utils/sbin/mount/xmalloc.h

## Scope

Declares fatal allocation and exit helpers for legacy mount code.

## API Surface

Exposes `xmalloc()`, `xrealloc()`, `xstrdup()`, `die()`, and the cleanup hook `at_die`.

## Dependencies And Risks

The header includes `sys/types.h` and `stdarg.h` but has no include guard. Multiple inclusion is harmless for these extern declarations, but the style differs from the other headers in this directory.
