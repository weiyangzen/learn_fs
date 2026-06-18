<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/xattr-utils.c -->
# sources/distributed-fs/orangefs/src/common/misc/xattr-utils.c

## Purpose
Provides a compatibility fallback for `fgetxattr` on platforms where the function is not available at build time.

## Important APIs, Types, And Functions
Conditionally defines `fgetxattr` with either the standard four-argument form or the extra-argument form selected by `HAVE_FGETXATTR_EXTRA_ARGS`. The fallback sets `errno = ENOSYS` and returns `-1`.

## Control Flow
Compilation is entirely feature-macro driven. If `HAVE_FGETXATTR` is absent, this file supplies the function body declared by `xattr-utils.h`; otherwise it contributes no runtime behavior.

## State And Persistence
No persistent state exists. The only state change is setting process-local `errno` when the stub is called.

## Dependencies And Integration Points
Includes standard C headers and `xattr-utils.h`. It lets code link on systems without native extended attribute support while preserving normal failure semantics.

## Risks And Test Signals
The main risk is configure macro mismatch causing a signature conflict with system headers. Tests should compile with and without `HAVE_FGETXATTR`, and runtime tests on unsupported platforms should observe `-1` plus `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/xattr-utils.c -->
