# File Research: sources/cow-pools/bcachefs-tools/linux/string.c

## Purpose
Small subset of Linux string/memory helpers.

## Key APIs
- `strim()` trims leading and trailing whitespace in place.
- `strlcpy()` copies with truncation and returns source length.
- `strscpy()` copies with Linux-style `-E2BIG` on truncation/invalid count.
- `memzero_explicit()` clears memory and uses `barrier_data()`.
- `match_string()` returns the index of a matching string or `-EINVAL`.
- `memscan()` returns pointer to first matching byte or end pointer.

## Dependencies
Uses libc ctype/string/errno/limits plus Linux bug/compiler/string headers.
