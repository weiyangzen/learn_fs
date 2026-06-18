<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-emacs-j -->
# sources/distributed-fs/openafs/src/tests/build-emacs-j

## Purpose
Parallel-build variant of the Emacs build stress test.

## Important APIs, Types, And Functions
Sets `MAKEFLAGS="-j"` and invokes `$srcdir/generic-build` for Emacs 20.7.

## Control Flow
Skips under `FAST`; otherwise runs the same build as `build-emacs` but with parallel make enabled.

## State And Persistence
Creates build artifacts and stresses concurrent metadata/data operations.

## Dependencies And Integration Points
Requires generic build harness, archive, and a toolchain. The parallelism stresses filesystem locking/cache consistency more than the serial variant.

## Risks And Test Signals
Race-sensitive and external-build dependent. Success is complete parallel build with exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-emacs-j -->
