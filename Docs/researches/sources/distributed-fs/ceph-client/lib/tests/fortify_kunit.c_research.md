
# sources/distributed-fs/ceph-client/lib/tests/fortify_kunit.c

## Purpose
`fortify_kunit.c` is a runtime test suite for `CONFIG_FORTIFY_SOURCE`. It verifies compile-time and dynamic object-size discovery, allocation size attributes, string helper bounds checks, memory helper bounds checks, and protected failure behavior.

## Important APIs, types, and functions
The file intentionally redefines `fortify_panic()` and `fortify_warn_once()` before including string headers so overflows increment KUnit counters instead of panicking. `fortify_add_kunit_error()` finds named KUnit resources for read/write overflow counters. Tests cover `__compiletime_strlen`, `__builtin_object_size`, `__builtin_dynamic_object_size`, `kmalloc`/`kcalloc`/`krealloc` families, `vmalloc`, `kvmalloc`, devm allocators, `kmemdup`, `strlen`, `strnlen`, `strcpy`, `strncpy`, `strscpy`, `strcat`, `strncat`, `strlcat`, `memcpy`, `memmove`, `memscan`, `memchr`, `memchr_inv`, and `memcmp`.

## Control flow
Suite init skips unless `CONFIG_FORTIFY_SOURCE` is enabled, resets counters, and registers them as KUnit resources. Allocation-size tests are macro-generated for constant and dynamic lengths; dynamic tests skip if the compiler lacks `__builtin_dynamic_object_size`. String and memory tests build padded structs so overflow attempts can be counted while confirming guard fields are not modified.

## State and persistence
Static resources and global counters track overflow classifications per test. Allocations are freed directly, through devm teardown, or by KUnit device cleanup. No durable state is produced.

## Dependencies and integration points
It depends on KUnit device/resource APIs, test-bug support, allocator APIs, string/memory fortify wrappers, vmalloc, and compiler builtins. The Makefile suppresses expected string warnings, unsequenced warnings, and structleak instrumentation effects.

## Risks and edge cases
The suite is highly compiler- and configuration-sensitive. It depends on include ordering and macro redefinition to intercept fortify behavior. Because it deliberately performs invalid operations under guarded wrappers, unrelated sanitizer or compiler changes can alter expected counters.

## Test signals
Pass means expected overflow counters increment and surrounding padding remains unchanged. Skips indicate missing `CONFIG_FORTIFY_SOURCE` or dynamic object-size builtin support for specific dynamic allocation tests.
