<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/xattr-utils.h -->
# sources/distributed-fs/orangefs/src/common/misc/xattr-utils.h

## Purpose
Normalizes extended-attribute header inclusion and `fgetxattr` prototype availability across Unix and Windows builds.

## Important APIs, Types, And Functions
Includes `<sys/xattr.h>` or `<attr/xattr.h>` when configured. On Windows it defines `ssize_t` as `size_t`. If no prototype is detected, it declares `fgetxattr` in either standard or extra-argument form.

## Control Flow
There is no runtime flow; preprocessor checks select the correct declaration path.

## State And Persistence
No state is defined. The header only affects compile-time API visibility.

## Dependencies And Integration Points
Depends on `pvfs2-internal.h` and configure macros. It is included by `xattr-utils.c` and any code needing portable `fgetxattr` access.

## Risks And Test Signals
Risks include platform ABI mismatches when configure probes are wrong and the Windows `ssize_t` typedef differing from signed POSIX semantics. Test signals are successful compilation on Linux xattr variants, macOS/BSD-like extra-argument configurations, and Windows builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/xattr-utils.h -->
