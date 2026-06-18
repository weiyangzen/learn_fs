# sources/distributed-fs/ceph-client/include/linux/fortify-string.h

## Purpose
This header implements Linux `FORTIFY_SOURCE` wrappers for common string and memory functions. It adds compile-time and runtime object-size checking while preserving sanitizer-aware underlying calls.

## APIs, types, and control flow
It defines fortify function ids, read/write reasons, panic/report hooks, compile-time overflow diagnostics, and object-size helper attributes (`POS`, `POS0`). Sanitizer branches map underlying `memcpy`, `memmove`, `memset`, string, and memory-search calls to builtins or ASAN/HWASAN/KMSAN implementations. Fortified wrappers cover `strncpy`, `strnlen`, `strlen`, `sized_strscpy`, `strlcat`, `strcat`, `strncat`, `memset`, `memcpy`, `memmove`, `memscan`, `memcmp`, `memchr`, `memchr_inv`, `kmemdup`, and `strcpy`. Control flow generally captures compile-time/dynamic object sizes, emits compile-time errors/warnings for constant violations, calls `fortify_panic()` for runtime overflows, then delegates to the underlying operation. `unsafe_memcpy()` intentionally bypasses checks but requires a justification argument.

## State and dependencies
No persistent state is stored here. Behavior depends heavily on compiler object-size support, sanitizer configuration, KUnit override hooks, warning level, and allocation hooks for `kmemdup`.

## Integration, risks, and tests
This header is globally sensitive because it macro-redefines core functions. Risks include false positives with flexible arrays, missing checks for unknown dynamic sizes, field-spanning copies that should use `struct_group()`, sanitizer aliasing mistakes, and hiding real bugs behind `unsafe_memcpy`. Tests should include KUnit panic/warn overrides, compile-fail overflow cases, runtime overflow detection, sanitizer builds, flexible-array cases, and return-value preservation on panic paths.
