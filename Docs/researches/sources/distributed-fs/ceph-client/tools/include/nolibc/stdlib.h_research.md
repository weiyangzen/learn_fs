# sources/distributed-fs/ceph-client/tools/include/nolibc/stdlib.h

## Purpose
Implements minimal stdlib functionality for nolibc: process abort, environment lookup, heap allocation, integer formatting, and string-to-integer conversion.

## APIs, Types, and Functions
Defines `struct nolibc_heap`, `abs/labs/llabs`, weak `abort`, `atol`, `atoi`, `free`, `getenv`, `malloc`, `calloc`, `realloc`, integer-to-string helpers `utoh_r`, `utoa_r`, `itoa_r`, `u64toa_r`, `i64toa_r` and buffer-returning variants, internal `_nolibc_u64toa_base`, parser `__strtox`, and `strtol`, `strtoul`, `strtoll`, `strtoull`, `strtoimax`, `strtoumax`.

## Control Flow, State, and Persistence
`malloc` maps heap chunks with `mmap` and prefixes them with `struct nolibc_heap`; `free` unmaps the whole chunk, and `realloc` allocates/copies/frees when needed. Environment lookup scans global `environ`. Numeric formatting repeatedly divides or uses reciprocal multiplication for bases, writing caller buffers or a shared static `itoa_buffer`. String conversion handles whitespace, sign, base autodetection, overflow limits, and end pointers.

## Dependencies and Integration
Depends on `arch.h`, `types.h`, `sys.h`, `string.h`, and Linux auxv definitions. It is used by stdio formatting, CRT startup, directory wrappers, and most higher-level nolibc helpers requiring heap or conversion support.

## Risks and Test Signals
Risks include one-mmap-per-allocation overhead, no allocator reuse, static conversion buffer not being thread-safe, overflow and base edge cases in `__strtox`, and `realloc` copy-size dependence on stored heap metadata. Test signals are malloc/calloc/realloc/free under ASan/strace, conversion boundary tests for every signed/unsigned limit, base 0/8/10/16 parsing, environment lookup, and concurrent calls to buffer-returning conversion helpers.
