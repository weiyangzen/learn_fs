# File Research: sources/cow-pools/bcachefs-tools/include/linux/bsearch.h

Purpose: inline binary search helper compatible with Linux `bsearch`-style usage.

Key contents:
- Defines `__inline_bsearch()` taking key, base pointer, element count, element size, and comparison callback.
- Iteratively probes the middle element, narrows the search, and returns the matching element pointer or `NULL`.

Important interactions:
- Depends on `cmp_func_t` from Linux types shims.
- Used by code wanting header-only bsearch without libc API mismatch.
