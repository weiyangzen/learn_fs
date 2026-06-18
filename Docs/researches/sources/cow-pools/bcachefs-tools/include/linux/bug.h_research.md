# File Research: sources/cow-pools/bcachefs-tools/include/linux/bug.h

Purpose: userspace equivalents for Linux build-time assertions, BUG, and WARN macros.

Key contents:
- Defines build-bug macros such as `BUILD_BUG_ON`, `BUILD_BUG_ON_ZERO`, and power-of-two checks.
- `BUG()` flushes stdout, asserts false, and marks unreachable.
- `BUG_ON()` maps to `assert(!(cond))`.
- `WARN`, `WARN_ON`, `WARN_ONCE`, and `WARN_ON_ONCE` print warning locations to stderr and return condition status.
- Optional Valgrind memory debugging hook under `CONFIG_VALGRIND`.

Important interactions:
- Used pervasively by shim and bcachefs code.
- In userspace, `BUG_ON` behavior depends on assertions, unlike kernel panic semantics.
