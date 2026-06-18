<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-gdb -->
# sources/distributed-fs/openafs/src/tests/build-gdb

## Purpose
Runs the generic build harness on GDB 5.0 as another large source-tree stress test.

## Important APIs, Types, And Functions
Shell wrapper around `$srcdir/generic-build` using `$AFSROOT/.../gdb-5.0.tar.gz`.

## Control Flow
Skips when `FAST` is set; otherwise delegates to generic-build.

## State And Persistence
Creates extracted source and build outputs.

## Dependencies And Integration Points
Depends on archive availability, compiler toolchain, and generic-build.

## Risks And Test Signals
Legacy GDB may not build on modern platforms. Success is generic-build exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-gdb -->
