# sources/distributed-fs/ceph-client/arch/x86/math-emu/reg_ld_str.c

## Purpose
Implements all math-emulator transfers between user memory and internal `FPU_REG` values, including load/store of extended, double, single, integer, packed BCD, environment, and full FPU save/restore images.

## Important APIs, Types, And Functions
Loaders include `FPU_load_extended()`, `FPU_load_double()`, `FPU_load_single()`, `FPU_load_int64()`, `FPU_load_int32()`, `FPU_load_int16()`, and `FPU_load_bcd()`. Stores include `FPU_store_extended()`, `FPU_store_double()`, `FPU_store_single()`, integer stores, and `FPU_store_bcd()`. Environment helpers are `fldenv()`, `FPU_frstor()`, `fstenv()`, and `fsave()`. `FPU_round_to_int()` performs integer rounding.

## Control Flow
Load paths wrap user-memory access with reentrancy checks, decode external formats, classify zeros, normals, denormals, infinities, and NaNs, normalize as needed, and set tags. Store paths branch on tag, round to target precision, raise underflow/overflow/precision/invalid exceptions according to the control word, write masked indefinite values where required, and finally copy bytes to user memory. Environment paths decode 14-byte or 28-byte formats depending on address mode, restore or derive tags, and serialize registers in stack order.

## State And Persistence
This file reads/writes user memory and heavily mutates emulator state: registers, tags, `control_word`, `partial_status`, `top`, instruction/operand addresses, and FPU stack contents. `fsave()` also calls `finit()`, making it a state-resetting operation.

## Dependencies And Integration Points
Depends on Linux `uaccess` primitives, FPU stack/tag macros, constants from `reg_constant.h`, control/status word definitions, normalization and shift helpers, and exception helpers. It is the bridge between architectural memory formats and emulator internals.

## Risks
User memory access can fault and the comment notes emulator static data may change while swapping, so reentrancy handling matters. Rounding edge cases for denormals, overflow, NaNs, unsupported encodings, and masked/unmasked exceptions are high risk. Integer minimum values and BCD overflow use special indefinite encodings. A notable review point is the `FPU_store_single()` empty-register branch checking `control_word & EX_Invalid`, while neighboring code generally uses `CW_Invalid`.

## Test Signals
Round-trip tests for float/double/extended, all integer widths, BCD, infinities, quiet/signaling NaNs, denormals, zero signs, precision modes, rounding modes, masked and unmasked exceptions, invalid stack stores, `fldenv/fstenv` in 16/32-bit modes, `frstor/fsave` register ordering, and user-copy fault paths.
