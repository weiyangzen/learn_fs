# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_add_sub.c

## Purpose
This file implements high-level add/subtract logic for emulator `FPU_REG` operands, handling sign, magnitude ordering, denormals, zeros, infinities, NaNs, destination selection, and x87 rounding/status behavior.

## Important APIs, Types, and Functions
Public functions are `FPU_add(FPU_REG const *b, u_char tagb, int deststnr, int control_w)` and `FPU_sub(int flags, int rm, int control_w)`. Static `add_sub_specials()` handles zeros, denormals, infinities, and invalid infinity-minus-infinity cases. Lower-level arithmetic is delegated to assembly helpers `FPU_u_add()` and `FPU_u_sub()`.

## Control Flow
`FPU_add()` compares tags. For two valid operands, same signs call unsigned add, opposite signs compare exponent/significand magnitude and call unsigned subtract in the correct order or produce signed zero based on rounding mode. Denormals are normalized after `denormal_operand()`. NaNs go through `real_2op_NaN()`. Special values fall into `add_sub_specials()`. `FPU_sub()` selects operands from ST0, ST(rm), or loaded memory data based on `REV`, `DEST_RM`, and `LOADED`; then applies similar magnitude/sign logic for subtraction and writes the chosen destination tag.

## State and Persistence
The file mutates destination FPU registers, tags, signs, and exception/status bits through helper calls. It preserves the original destination sign if a lower-level operation returns an error.

## Dependencies and Integration Points
It is called by register arithmetic handlers, memory arithmetic in `fpu_entry.c`, and other helpers needing addition/subtraction. It depends on constants, exception handling, denormal conversion, register tag helpers, and unsigned assembly arithmetic.

## Risks and Test Signals
Risks include magnitude comparison errors, wrong signed-zero result under `RC_DOWN`, flag misinterpretation for loaded/reversed/destination-register forms, and special-case divergence from x87. Test signals include exhaustive add/sub instruction forms, signed-zero tests under all rounding modes, NaN/infinity/denormal combinations, and comparison to hardware x87.
