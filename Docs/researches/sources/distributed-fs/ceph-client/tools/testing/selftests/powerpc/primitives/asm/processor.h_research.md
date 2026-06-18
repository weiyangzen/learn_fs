# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/processor.h

## Purpose
`processor.h` is an intentionally empty compatibility shim in the primitives selftest include tree. It satisfies kernel-header include paths copied into userspace tests without pulling in the full kernel implementation.

## Important APIs, Types, and Functions
It declares no APIs, types, macros, or functions. Its important behavior is absence: source files can include the header and continue compiling because the specific test does not require the omitted definitions.

## Control Flow and State
There is no runtime control flow and no state.

## Dependencies and Integration Points
It integrates with local copies of powerpc kernel headers such as `ppc_asm.h` and `word-at-a-time.h`, preserving include compatibility for the primitives directory.

## Risks and Test Signals
The risk is that future copied kernel code may start needing real definitions from this header, causing build failures or incorrect stubs. The test signal is successful compilation of `load_unaligned_zeropad` and related primitive tests with the shim still empty.
