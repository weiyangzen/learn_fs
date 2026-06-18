# sources/distributed-fs/ceph-client/arch/powerpc/tools/gcc-check-mprofile-kernel.sh

## Purpose
This compiler probe checks whether a ppc64 ELFv2 toolchain supports `-mprofile-kernel` correctly for kernel profiling and respects the `notrace` attribute.

## Important APIs, Types, And Functions
It receives the compiler invocation as `$*`, forces `-m64 -mabi=elfv2`, compiles small C snippets with `-S -x c -O2 -p -mprofile-kernel`, searches for `_mcount`, and includes `<linux/compiler.h>` to test `notrace`.

## Control Flow
The first compile must produce an `_mcount` call. The second compile marks the function `notrace`; if `_mcount` still appears, the script exits with status 1. Otherwise it exits zero.

## State And Persistence
The script writes no files and keeps no state.

## Dependencies And Integration Points
It depends on bash, the configured compiler, kernel include paths supplied by the caller environment, and assembly naming conventions. It is used as a build-time feature check before enabling mprofile-based tracing.

## Risks
It is valid only for 64-bit ELFv2 and can be misleading for other targets. Assembly output differences or missing include paths can cause false negatives. The second test's failure condition is inverted through `grep ... && exit 1`, so changes should preserve that logic.

## Test Signals
Zero exit means `_mcount` is emitted for normal functions and suppressed for `notrace`; nonzero means the feature should not be enabled.
