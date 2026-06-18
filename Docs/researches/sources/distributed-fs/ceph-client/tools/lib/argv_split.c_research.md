<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/argv_split.c -->
# sources/distributed-fs/ceph-client/tools/lib/argv_split.c

## Purpose
`argv_split.c` provides a small helper to split a whitespace-separated string into a NULL-terminated `argv` array. It mirrors a common kernel helper but is built for userspace tools.

## Important APIs, types, and functions
Private helpers are `skip_arg()` and `count_argc()`. Public functions are `argv_split(const char *str, int *argcp)` and `argv_free(char **argv)`. It uses Linux-style `skip_spaces()`, `isspace()`, and `strndup()`.

## Control flow
`argv_split()` first counts arguments by skipping leading whitespace and scanning to the next whitespace. It allocates `argc + 1` pointers, optionally stores `argc`, duplicates each token with `strndup()`, and terminates the array with NULL. On allocation failure it frees any partially built vector through `argv_free()`.

## State and persistence behavior
All returned state is heap-owned by the caller and freed with `argv_free()`. There is no global state and no quote/escape parsing state.

## Dependencies and integration points
It depends on `tools/include/linux` compatibility headers for kernel-like string and ctype helpers. Tool parsers can use it when their syntax is simple whitespace tokenization.

## Risks and edge cases
Quotes, backslashes, and shell-like escaping are deliberately not honored. If `calloc()` fails, `argcp` is left unchanged because it is assigned only after allocation success. `argv_free()` assumes a non-NULL, NULL-terminated vector; passing NULL would dereference it.

## Test signals
Test empty strings, leading/trailing whitespace, repeated whitespace, tabs/newlines, quoted text showing non-shell behavior, allocation-failure cleanup, and `argv_free()` nulling element pointers before freeing the vector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/argv_split.c -->
