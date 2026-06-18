# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_trig.c

## Purpose
This file implements x87 transcendental and miscellaneous ST0/ST1 instructions such as `f2xm1`, `fptan`, `fxtract`, `fsqrt`, `fsin`, `fcos`, `fsincos`, `fprem`, `fyl2x`, `fpatan`, `fyl2xp1`, `fscale`, and stack pointer adjustments.

## Important APIs, Types, and Functions
Public dispatchers are `FPU_triga()` and `FPU_trigb()`, backed by `trig_table_a` and `trig_table_b`. Major static helpers include `trig_arg()`, `rem_kernel()`, `do_fprem()`, `convert_l2reg()`, `single_arg_error()`, `single_arg_2_error()`, `f2xm1()`, `fptan()`, `fxtract()`, `fsqrt_()`, `frndint_()`, `f_sin()`, `f_cos()`, `fsincos()`, `fyl2x()`, `fpatan()`, `fyl2xp1()`, and `fscale()`.

## Control Flow
The dispatchers call a handler selected by `FPU_rm`. Trigonometric handlers reduce arguments with `trig_arg()`, call polynomial helpers, adjust quadrant/sign, and set precision flags. Remainder instructions use `do_fprem()` and `rem_kernel()` to compute exact-ish remainders and quotient condition bits. Log/atan paths validate ST0/ST1 combinations, handle NaN/infinity/zero/denormal priority, call polynomial kernels, and pop ST0 when instruction semantics require it. `fscale()` rounds ST1 toward zero, adjusts ST0's exponent, and invokes normal rounding/exception handling.

## State and Persistence
The file heavily mutates ST0/ST1 register values, tags, top pointer, condition codes, precision/denormal/invalid/overflow/underflow status, and the control word temporarily for internal chopping operations. It restores saved control/status state around internal computations where hardware-visible flags should not leak.

## Dependencies and Integration Points
It depends on register constants, core arithmetic helpers, polynomial approximation files, fixed-point `Xsig` assembly helpers, exception/status/control logic, and tag helpers. It is reached from `fpu_entry.c` for `D9 E8..FF` and related opcode groups.

## Risks and Test Signals
Risks include argument reduction inaccuracies near large powers, quadrant/sign mistakes, exception priority mismatches, stack pop/push errors, and divergence from 80486 quirks. Test signals include transcendental instruction suites over finite/zero/denormal/infinity/NaN inputs, quotient condition bits for `fprem/fprem1`, comparison to hardware x87, and PARANOID internal error coverage.
