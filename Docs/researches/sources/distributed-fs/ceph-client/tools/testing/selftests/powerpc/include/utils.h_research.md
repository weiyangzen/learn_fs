# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/utils.h

## Purpose
Common C utility header for PowerPC selftests, providing result macros, parsing, binding, hardware capability checks, timing, and syscall helpers.

## Important APIs, Types, and Functions
Defines FAIL/SKIP macros, `ARRAY_SIZE`, binding constants, hardware capability predicates, timebase helpers, parsing/read/write helpers, perf/syscall wrappers, and signal-handler push/pop declarations used across tests.

## Control Flow
Most content is inline helpers/macros; callers use them to skip unsupported hardware, fail with messages, bind CPUs, read sysfs/proc numeric values, and measure time.

## State and Persistence
Some helpers mutate process affinity, signal handlers, or target sysfs files when called. The header itself persists no state.

## Dependencies and Integration Points
Included throughout PowerPC selftests and paired with `../utils.c` in targets that need non-inline implementations.

## Risks and Test Signals
Risk is that utility macros exit from deep call sites, so cleanup must be handled by callers. Test signals are consistent skip/fail behavior and correct feature detection.
