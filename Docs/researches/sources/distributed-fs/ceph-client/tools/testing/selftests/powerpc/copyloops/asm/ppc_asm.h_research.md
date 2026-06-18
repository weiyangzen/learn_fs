# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/ppc_asm.h

## Purpose
Provides local PowerPC assembly macro compatibility for copied kernel memory/copy-user loops.

## Important APIs, Types, and Functions
Defines register aliases, stack frame constants, `_GLOBAL*` wrappers that prefix symbols with `test_`, `CFUNC`, `PPC_MTOCRF`, `EX_TABLE`, feature-section no-op macros, and `DCBT_SETUP_STREAMS` as empty.

## Control Flow
No runtime control flow. Preprocessor expansion maps kernel assembly annotations and exception-table directives to forms accepted in the selftest binary.

## State and Persistence
No state is stored; generated symbols and sections affect build/link output only.

## Dependencies and Integration Points
Includes `<ppc-asm.h>` and is consumed by copyloop `.S` files. It is a critical integration layer between kernel assembly source style and userspace selftest linking.

## Risks and Test Signals
Risk is semantic drift from kernel macros, especially exception table and feature patching behavior. Build/link success plus validation tests provide coverage.
