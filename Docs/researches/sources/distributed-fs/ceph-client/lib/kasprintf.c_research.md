# sources/distributed-fs/ceph-client/lib/kasprintf.c

Purpose: implements kernel allocation-backed printf helpers and a const-string optimization variant.

Important APIs: `kvasprintf()`, `kvasprintf_const()`, and `kasprintf()`. `kvasprintf()` computes formatted length, allocates with `kmalloc_track_caller()`, formats into the buffer, and warns if two `vsnprintf()` passes disagree. `kvasprintf_const()` avoids allocation or copying when the format is literal/no-percent or exactly `%s` and the string can be represented by `kstrdup_const()`.

Control flow: `kasprintf()` wraps varargs around `kvasprintf()`. `kvasprintf()` uses `va_copy()` for the sizing pass and the original `va_list` for the formatting pass. `kvasprintf_const()` may consume a string argument when handling `%s`.

State and persistence: returns allocated or const-managed string memory owned by the caller; `kvasprintf_const()` results must be released with `kfree_const()`.

Dependencies and integration: depends on slab allocation, string helpers, and export macros. Kobject naming uses `kvasprintf_const()` to avoid unnecessary allocations for static names.

Risks: callers must use the correct free routine for const-optimized results; formatting side effects or unstable arguments can trigger mismatched `vsnprintf()` sizes; allocation failure returns NULL.

Test signals: allocation failure injection, `%s` rodata optimization checks, and callers validating `kfree_const()` behavior.
