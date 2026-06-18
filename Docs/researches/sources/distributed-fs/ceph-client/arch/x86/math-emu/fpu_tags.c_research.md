# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_tags.c

## Purpose
This file manages the x87 emulator tag word, stack top, special value classification, and register-copy helpers.

## Important APIs, Types, and Functions
Functions include `FPU_pop()`, `FPU_gettag0()`, `FPU_gettagi()`, `FPU_gettag()`, `FPU_settag0()`, `FPU_settagi()`, `FPU_settag()`, `FPU_Special()`, `isNaN()`, `FPU_empty_i()`, `FPU_stackoverflow()`, `FPU_copy_to_regi()`, `FPU_copy_to_reg1()`, and `FPU_copy_to_reg0()`.

## Control Flow
Tag accessors compute the physical register index from `top` plus logical stack offsets. `FPU_pop()` marks the current top empty and increments top. Special classification maps exponent/significand patterns to denormal, infinity, or NaN. Copy helpers copy a full `FPU_REG` and set the target tag in the same operation.

## State and Persistence
The file mutates persistent per-task `fpu_tag_word`, `top`, and register stack contents. There is no file-local state.

## Dependencies and Integration Points
It is used by nearly all emulator instruction handlers. It depends on `fpu_emu.h`, `fpu_system.h`, and exception constants for tag values and exponent interpretation.

## Risks and Test Signals
Risks include tag-word corruption, stack wrap mistakes, and misclassification of pseudo-denormals or unsupported NaNs. Test signals include stack push/pop instruction tests, `fxam`, save/restore tag-word tests, and edge values for zero, denormal, infinity, and NaN.
