# sources/cloud-native/composefs/libcomposefs/lcfs-utils.h

## Purpose
`lcfs-utils.h` provides small utility macros and inline helpers for libcomposefs: min/max, prefix checks, memory duplication, overflow-safe reallocarray fallback, hex parsing, cleanup attributes, fd cleanup, pointer stealing, basename extraction, and digest conversion declarations.

## Important APIs, Types, And Functions
Important helpers are `str_has_prefix`, `memdup`, `size_multiply_overflow`, fallback `reallocarray`, `hexdigit`, `str_join`, `PROTECT_ERRNO`, `cleanup_freep`, `cleanup_fdp`, `steal_pointer`, and `gnu_basename`. It also declares `digest_to_string` and `digest_to_raw`.

## Control Flow
Most helpers are inline single-purpose building blocks. Cleanup attributes close fds or free memory automatically at scope exit while preserving errno. `steal_pointer` transfers cleanup-managed ownership by nulling the source pointer.

## State And Persistence
No persistent state. It strongly affects local ownership and error preservation patterns across the library.

## Dependencies And Integration Points
Included by writer, EROFS writer, mount, and utility code. Meson config controls whether the fallback `reallocarray` is active.

## Risks
`max`/`min` macros evaluate arguments more than once. The type-safe `steal_pointer` macro shadows the inline function intentionally and can surprise static analysis. Cleanup helpers assume initialized pointers/fds.

## Test Signals
Indirectly covered everywhere. Error-path tests and valgrind setup in Meson are useful for validating cleanup behavior.
