# sources/distributed-fs/ceph-client/scripts/include/xalloc.h

## Purpose
Provides fail-fast allocation wrappers for host utilities.

## APIs, Control Flow, and State
`xmalloc()`, `xcalloc()`, `xrealloc()`, `xstrdup()`, and `xstrndup()` call the matching libc allocator and `exit(1)` on null results. They return allocated memory on success and do not print diagnostics.

## Dependencies and Integration
It includes `stdlib.h` and `string.h`. Tools such as `kallsyms.c` use it to simplify error handling in build-time utilities.

## Risks and Test Signals
The wrappers treat `malloc(0)` returning null as fatal, unlike some local wrappers elsewhere. They also make cleanup impossible on OOM. Test signals are host-tool compile coverage and intentional OOM handling expectations documented by callers.
