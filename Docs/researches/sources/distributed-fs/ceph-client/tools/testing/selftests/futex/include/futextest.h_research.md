<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/futextest.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/futextest.h

## Purpose
This header is the classic futex test library, providing raw futex syscall wrappers and atomic helpers independent of glibc abstractions.

## Important APIs, Types, And Functions
It defines `futex_t`, `FUTEX_INITIALIZER`, fallback futex op constants, `SYS_futex` time64 compatibility selection, the `futex()` syscall macro, wrappers for wait/wake/bitset/PI/wake-op/requeue/requeue-PI operations, and helpers `futex_cmpxchg()`, `futex_dec()`, `futex_inc()`, and `futex_set()`.

## Control Flow
All futex operation wrappers forward to `syscall(SYS_futex, ...)` with operation flags ORed into the op. Atomic helpers use GCC builtins or direct assignment.

## State And Persistence
The header owns no state; it mutates caller-supplied futex words and interacts with kernel futex wait queues.

## Dependencies And Integration Points
It integrates all classic futex functional tests with the Linux futex syscall ABI and handles 32-bit time64 build modes.

## Risks
The macro signature is intentionally loose because futex arguments are overloaded; type mistakes can compile. Fallback op definitions must stay correct. `futex_set()` is a plain assignment.

## Test Signals
All classic futex binaries should compile regardless of libc futex wrappers and observe expected syscall return counts/errno values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/include/futextest.h -->
