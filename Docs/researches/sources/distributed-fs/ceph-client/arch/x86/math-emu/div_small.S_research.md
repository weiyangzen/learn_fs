# sources/distributed-fs/ceph-client/arch/x86/math-emu/div_small.S

## Purpose
This assembly file implements a small helper to divide a 64-bit unsigned integer in place by a 32-bit unsigned denominator and return the remainder.

## Important APIs, Types, and Functions
The exported function is `FPU_div_small(unsigned long long *x, unsigned long y)`. It uses the i386 `divl` instruction twice, first for the high word and then for the low word.

## Control Flow
The function loads the high 32 bits, divides by `y` with zero high dividend, stores the high quotient, then divides the low 32 bits using the previous remainder in `%edx`, stores the low quotient, and returns the final remainder in `%eax`.

## State and Persistence
There is no global state. The 64-bit integer pointed to by `x` is overwritten with the quotient, and the remainder is returned.

## Dependencies and Integration Points
It depends on 32-bit x86 calling convention macros and is declared in `fpu_emu.h`. Other emulator conversion or rounding code can use it for decimal/integer scaling.

## Risks and Test Signals
Risks include divide-by-zero or quotient overflow if callers violate preconditions. Test signals include integer conversion tests, BCD load/store paths, and emulator builds with assembly helper linkage.
