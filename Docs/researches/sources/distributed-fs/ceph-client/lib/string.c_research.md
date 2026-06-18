# sources/distributed-fs/ceph-client/lib/string.c

## Purpose
Provides generic fallback implementations for core kernel string and memory primitives that may be replaced by architecture-specific versions or FORTIFY wrappers. It includes libc-like operations plus `sized_strscpy()` and byte scanning helpers used broadly across the kernel.

## APIs, Control Flow, and State
Conditionally exported fallbacks include `strncasecmp()`, `strcasecmp()`, `strcpy()`, `strncpy()`, `stpcpy()`, `strcat()`, `strncat()`, `strlcat()`, `strcmp()`, `strncmp()`, `strchr()`, `strchrnul()`, `strrchr()`, `strnchr()`, `strlen()`, `strnlen()`, `strspn()`, `strcspn()`, `strpbrk()`, `strsep()`, `memset()`, `memset16()`, `memset32()`, `memset64()`, `memcpy()`, `memmove()`, `memcmp()`, `bcmp()`, `memscan()`, `strstr()`, `strnstr()`, `memchr()`, and `memchr_inv()`. `sized_strscpy()` is an important bounded copy helper using word-at-a-time scanning where alignment and memory-safety configuration allow it, forcing NUL termination and returning `-E2BIG` on truncation or bad sizes. Memory routines are simple byte or word loops except `memcmp()` and `memchr_inv()`, which use word-sized optimizations under suitable architecture conditions.

There is no persistent state. The file is built with `__NO_FORTIFY` so it can provide low-level primitives beneath fortified wrappers.

## Dependencies, Integration, Risks, and Tests
Depends on ctype, errno, word-at-a-time helpers, unaligned access helpers, endian/page definitions, architecture `__HAVE_ARCH_*` selection, and export support. Integration is universal: nearly every subsystem may link to these fallbacks when no architecture override exists. Risks include unsafe legacy APIs such as `strcpy()`/`strcat()`, overlap misuse with `memcpy()`, `strlcat()` BUG when destination length exceeds count, word-at-a-time reads near page boundaries, KMSAN false positives if optimizations are not disabled, and callers misinterpreting `sized_strscpy()` return values. Test signals include string/memory selftests, FORTIFY tests, KASAN/KMSAN coverage, cross-architecture builds with and without efficient unaligned access, and fuzzing around truncation and NUL boundary cases.
