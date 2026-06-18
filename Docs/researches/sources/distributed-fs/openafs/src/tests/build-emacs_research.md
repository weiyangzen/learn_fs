<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-emacs -->
# sources/distributed-fs/openafs/src/tests/build-emacs

## Purpose
Runs the generic build harness on Emacs 20.7 as a large filesystem/build stress test.

## Important APIs, Types, And Functions
Shell wrapper around `$srcdir/generic-build` with `$AFSROOT/.../emacs-20.7.tar.gz`.

## Control Flow
Skips when `FAST` is set; otherwise invokes the generic build script with optional shell verbosity.

## State And Persistence
Creates unpacked source, object, and build outputs as determined by `generic-build`.

## Dependencies And Integration Points
Requires `$srcdir`, `$AFSROOT`, shell, compiler toolchain, and the archive.

## Risks And Test Signals
Old source may not build on modern systems. Success is generic-build exit `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/build-emacs -->
