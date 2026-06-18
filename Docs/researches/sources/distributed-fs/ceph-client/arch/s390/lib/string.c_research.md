# sources/distributed-fs/ceph-client/arch/s390/lib/string.c

## Purpose
Provides optimized s390 C/inline-assembly implementations of string and memory search/compare helpers selected by architecture feature macros.

## Important APIs, Types, And Functions
Conditionally exports `strlen`, `strnlen`, `strcat`, `strlcat`, `strncat`, `strcmp`, `strstr`, `memchr`, `memcmp`, and `memscan`. Internal helpers `__strend()` and `__strnend()` find NUL terminators with `srst`; `clcle()` compares length-bounded byte ranges.

## Control Flow And State
String-end searches loop on s390 string-search instructions until completion. Concatenation finds the destination end, then uses `mvst` or `memcpy` to append. Comparisons use `clst` or `clcle` and translate condition codes into standard C return values. `memchr`/`memscan` search for a byte and return either the match, NULL, or one-past-end depending on API semantics.

## Dependencies And Integration
Depends on architecture string configuration macros, s390 inline assembly condition-code helpers, exported kernel string APIs, and generic `memcpy` from `mem.S` for some append operations.

## Risks And Test Signals
Risks include wrong return semantics for not-found cases, buffer-bound handling in `strlcat`/`strncat`, condition-code translation, and interaction with fortified string wrappers disabled for this implementation. Signals include lib/string tests, fortify build checks, boot/runtime string-heavy workloads, and comparison with generic implementations.
