# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/asm-compat.h

## Purpose
`asm-compat.h` provides assembler compatibility macros that let copied powerpc kernel assembly headers build in the selftest environment across 32-bit and 64-bit modes.

## Important APIs, Types, and Functions
Key macros include `PPC_LL`, `PPC_STL`, `PPC_STLU`, compare aliases, `PPC_LONG`, `PPC_LONG_ALIGN`, `PPC_TLNEI`, `PPC_LLARX`, and `PPC_STLCX`. They abstract load/store width and directive differences.

## Control Flow and State
The file has no runtime flow. At assembly/preprocess time it selects instruction mnemonics and data directives based on word size and build defines.

## Dependencies and Integration Points
It is included by `ppc_asm.h` and other local kernel-header copies used by assembly or inline-assembly primitive tests.

## Risks and Test Signals
Risks are incorrect width selection, missing macro aliases for a compiler mode, and divergence from kernel headers. Signals are successful assembly of `loop.S`, `ptrace-gpr.S`, and primitive code under the intended 64-bit selftest build.
