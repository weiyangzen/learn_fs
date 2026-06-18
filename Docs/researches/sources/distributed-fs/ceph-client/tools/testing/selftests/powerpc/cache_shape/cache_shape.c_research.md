# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/cache_shape/cache_shape.c

## Purpose
Prints and validates cache shape auxiliary-vector entries exposed to userspace.

## Important APIs, Types, and Functions
Defines AT_* cache constants, `print_size()`, `print_geo()`, `test_cache_shape()`, and `main()`.

## Control Flow
`test_cache_shape()` reads cache size/geometry auxv values, prints human-readable cache size and line/associativity geometry, and is run through `test_harness()`.

## State and Persistence
Read-only process auxv state is used; no files are modified.

## Dependencies and Integration Points
Depends on ELF auxv definitions, libc auxv access, and PowerPC utility harness.

## Risks and Test Signals
Risk is platform variability or missing auxv entries. Test signal is successful decoding and printed cache topology information.
