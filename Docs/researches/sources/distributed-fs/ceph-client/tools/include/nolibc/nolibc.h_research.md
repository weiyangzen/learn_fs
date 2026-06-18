# sources/distributed-fs/ceph-client/tools/include/nolibc/nolibc.h

## Purpose
Top-level umbrella header for nolibc, a tiny libc-like layer for Linux programs that use raw syscalls and header-only helpers.

## APIs, Types, and Functions
Includes the ordered nolibc components: compiler support, standard integer/types, architecture backend, syscall layer, file/time/string/stdio/stdlib wrappers, and related compatibility headers. It defines `_NOLIBC_H` and `NOLIBC`.

## Control Flow, State, and Persistence
There is no runtime control flow in the umbrella itself. Its include order establishes the compile-time dependency graph so prototypes, typedefs, syscall macros, and startup helpers are visible before consumers use them.

## Dependencies and Integration
Depends on Linux UAPI headers and all sibling nolibc headers. It is the common include for tests and small utilities that want a libc-like API without linking libc.

## Risks and Test Signals
Risks include include-order regressions, duplicate definitions when mixed with system libc headers, and broad namespace exposure. Test signals are building representative programs by including only `nolibc.h`, include-what-you-use checks for individual headers, and mixed include-order smoke tests.
