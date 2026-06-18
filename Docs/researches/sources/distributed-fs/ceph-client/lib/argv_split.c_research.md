<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/argv_split.c -->
# sources/distributed-fs/ceph-client/lib/argv_split.c

## Purpose
Provides a small helper for splitting a whitespace-delimited kernel string into a NULL-terminated argv-style array.

## APIs, Types, and Functions
Exports `argv_split(gfp_t gfp, const char *str, int *argcp)` and `argv_free(char **argv)`. Internal `count_argc()` counts transitions from whitespace to non-whitespace using `isspace()`.

## Control Flow, State, and Persistence
`argv_split()` copies the source with `kstrndup(..., KMALLOC_MAX_SIZE - 1)` to avoid races with mutable sysctl/user-provided backing storage, counts tokens, allocates `argc + 2` pointers, stores the backing string in the hidden pointer immediately before the returned argv, then walks the copy, replacing whitespace with NUL bytes and recording starts of tokens. `argv_free()` expects the returned pointer, steps back one slot, frees the backing string, then frees the pointer array. There is no persistent state.

## Dependencies and Integration
Depends on kernel ctype, slab allocation, string helpers, and export support. Callers are kernel parsers that need simple whitespace splitting without shell quoting.

## Risks and Test Signals
Risks include callers forgetting to use `argv_free()`, passing a pointer not returned by `argv_split()` to `argv_free()`, expecting quote or escape handling, and very large input allocation failure. Test signals include empty/whitespace-only input, multiple whitespace classes, embedded tabs/newlines, NULL `argcp`, allocation-failure injection, and round-trip freeing under KASAN/KMEMLEAK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/argv_split.c -->
