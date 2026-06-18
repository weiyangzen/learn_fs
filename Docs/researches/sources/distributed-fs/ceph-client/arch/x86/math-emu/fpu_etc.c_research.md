# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_etc.c

## Purpose
This file implements a small group of single-register x87 instructions: change sign, absolute value, test, and examine.

## Important APIs, Types, and Functions
The public dispatcher is `FPU_etc()`, using `fp_etc_table`. Static handlers are `fchs()`, `fabs()`, `ftst_()`, `fxam()`, and `FPU_ST0_illegal()`.

## Control Flow
`FPU_etc()` indexes the handler table with `FPU_rm` and passes `st(0)` plus its tag. `fchs()` toggles the sign bit and `fabs()` clears it when ST0 is not empty. `ftst_()` sets condition codes based on zero, sign, denormal, NaN, infinity, or empty cases and raises exceptions where required. `fxam()` classifies ST0 into x87 condition bits and includes the sign in C1.

## State and Persistence
The file mutates ST0 sign bits, condition-code bits in `partial_status`, and exception status. It has no file-local persistent state.

## Dependencies and Integration Points
It is dispatched from `fpu_entry.c` for `D9 E0..E7`-style opcodes. It depends on tag classification, status-word macros, exception helpers, and register constants.

## Risks and Test Signals
Risks include incorrect condition-code encodings, denormal exception priority, and 80486 compatibility quirks. Test signals include `fchs`, `fabs`, `ftst`, and `fxam` instruction tests across zero, finite, denormal, infinity, NaN, and empty-stack inputs.
