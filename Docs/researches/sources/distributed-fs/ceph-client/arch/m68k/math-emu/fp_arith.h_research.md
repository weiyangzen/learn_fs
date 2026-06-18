# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_arith.h

## Purpose
Declares the C arithmetic kernels used by the m68k floating-point emulator dispatch layer.

## APIs, Flow, And State
The header exposes functions operating on `struct fp_ext *dest` and `struct fp_ext *src`: `fp_fabs`, `fp_fneg`, `fp_fadd`, `fp_fsub`, `fp_fcmp`, `fp_ftst`, `fp_fmul`, `fp_fdiv`, `fp_fsglmul`, `fp_fsgldiv`, `fp_fmod`, `fp_frem`, `fp_fint`, `fp_fintrz`, and `fp_fscale`. It defines no state or inline behavior.

## Dependencies And Integration
Requires the `struct fp_ext` definition from `fp_emu.h`/`asm/math-emu.h` before use. Included by `fp_arith.c` and other C math modules, while assembly dispatch references the compiled symbols directly.

## Risks And Test Signals
The ABI is pointer-based and mutating; callers must know operand ordering used by the emulator, especially for divide, modulo, and subtract. Compile-time coverage catches declaration drift; runtime instruction tests verify that dispatch table entries match the intended prototype and operand convention.
