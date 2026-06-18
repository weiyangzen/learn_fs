# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_string.c

String utility compatibility for FreeBSD SPL.

Key behavior:
- Provides `strpbrk()` implementation.
- `strident_canon()` converts a string into a valid C identifier by replacing invalid characters with `_` and forcing NUL termination.
- `kmem_asprintf()` allocates a formatted string from kmem.
- `kmem_strfree()` frees such strings using their runtime length.
- `kmem_scnprintf()` wraps `vsnprintf()` but returns the number of characters actually stored, capped at `size - 1`, to support safe follow-on string operations.

The file uses simple local digit/alpha classification macros.
