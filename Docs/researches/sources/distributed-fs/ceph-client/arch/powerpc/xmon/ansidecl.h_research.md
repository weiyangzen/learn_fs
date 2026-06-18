# sources/distributed-fs/ceph-client/arch/powerpc/xmon/ansidecl.h

## Purpose
`ansidecl.h` provides legacy ANSI/traditional C compatibility macros imported from old GNU code so the xmon disassembler sources can compile in the kernel tree.

## Important APIs, Types, And Functions
Macros include `PTR`, `PTRCONST`, `LONG_DOUBLE`, `AND`, `NOARGS`, `CONST`, `VOLATILE`, `SIGNED`, `DOTS`, `EXFUN`, `DEFUN`, `DEFUN_VOID`, `PROTO`, `PARAMS`, and `ANSI_PROTOTYPES`. The header selects ANSI definitions when `__STDC__`, `_AIX`, certain MIPS SVR4 modes, or `WIN32` are defined; otherwise it falls back to traditional C forms.

## Control Flow
There is no runtime control flow. Preprocessor conditionals expand declarations and function definitions differently depending on compiler mode.

## State And Persistence
The header has no state and no persistence.

## Dependencies And Integration Points
It is included by `ppc-dis.c` and supports binutils-derived headers and code such as `ppc.h`. In a modern kernel build, the ANSI branch is expected.

## Risks
These macros are obsolete and can conflict with kernel style or names if included broadly. The non-ANSI branch redefines `const` when missing and should remain isolated to the imported disassembler code. Changes can break compatibility with `ppc.h` declarations.

## Test Signals
Successful xmon disassembly builds are the main signal. Because runtime behavior is preprocessor-only, compile failures in `ppc-dis.c` or `ppc-opc.c` reveal regressions.
