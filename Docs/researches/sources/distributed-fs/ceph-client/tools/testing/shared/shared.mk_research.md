<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/shared.mk -->
# sources/distributed-fs/ceph-client/tools/testing/shared/shared.mk

## Purpose

`shared.mk` is the common build fragment for userspace tests that import kernel data-structure code.

## Important APIs, Types, and Functions

It sets include paths into `../shared`, tools headers, arch headers, and kernel `lib`; enables debug and sanitizer flags; links pthread and liburcu; defines shared object lists; generates `radix-tree.c` and `idr.c` by stripping static/inline qualifiers; and creates generated headers `autoconf.h`, `map-shift.h`, and `bit-length.h`. It supports `SHIFT`, `BUILD=32`, and `LONG_BIT` overrides.

## Control Flow and State

Make rules generate compatibility files when inputs or parameters change. Generated state lives under `generated/`. Object dependencies force rebuilds when shared headers or imported kernel sources change.

## Dependencies and Integration Points

It depends on `Makefile.arch`, GCC/Clang-compatible sanitizer flags, pthreads, liburcu, kernel source paths, and standard shell utilities. It is included by tests such as `tools/testing/vma/Makefile`.

## Risks and Test Signals

Risks include sed transformations changing kernel semantics, stale generated headers when `SHIFT` or bitness changes, missing sanitizer libraries, and include path drift. A successful sanitized build of xarray/maple/radix/VMA tests is the validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/shared.mk -->
