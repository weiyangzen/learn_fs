# sources/distributed-fs/ceph-client/include/linux/bitops.h

## Purpose
`bitops.h` is the generic front door for Linux bit operations. It ties together type-sized bit counting, architecture bitops, pure-C constant-foldable bitops, rotates, sign extension, order calculations, parity, first-set helpers, and atomic-looking compare/exchange mask helpers.

## Important APIs, Types, And Functions
Size conversion macros are `BITS_TO_LONGS()`, `BITS_TO_U64()`, `BITS_TO_U32()`, `BITS_TO_BYTES()`, and `BYTES_TO_BITS()`. Software Hamming weight functions are declared as `__sw_hweight8/16/32/64()`, with `hweight_long()` selecting 32- or 64-bit counting. The `bitop()` macro routes `__set_bit()`, `__clear_bit()`, `__change_bit()`, test-and-modify variants, `test_bit()`, and `test_bit_acquire()` to compile-time C helpers when possible and otherwise to normal architecture operations.

The header exports rotate helpers `rol64()`/`ror64()`, `rol32()`/`ror32()`, `rol16()`/`ror16()`, and `rol8()`/`ror8()`, sign extension helpers `sign_extend32()` and `sign_extend64()`, order helpers `get_bitmask_order()`, `get_count_order()`, and `get_count_order_long()`, `fls_long()`, `parity8()`, `__ffs64()`, `fns()`, and assignment/pointer-bit macros `assign_bit()`, `__assign_bit()`, `__ptr_set_bit()`, `__ptr_clear_bit()`, and `__ptr_test_bit()`. Under `__KERNEL__`, `set_mask_bits()` and `bit_clear_unless()` update words with `READ_ONCE()` plus `try_cmpxchg()`.

## Control Flow And State
The main control pattern is dispatch through `bitop()`: if the bit number, address non-nullness, and referenced word value are compile-time constants, the macro invokes a `const*` implementation from generic non-atomic bitops; otherwise it invokes the runtime operation. This preserves architecture behavior while allowing constants to optimize into immediate expressions. Rotates mask the shift count and use complementary shifts, avoiding undefined full-width shifts. `parity8()` folds the byte into four bits and indexes a parity constant. `set_mask_bits()` and `bit_clear_unless()` loop until a compare/exchange succeeds or until the test mask blocks clearing.

## Dependencies And Integration Points
The header depends on `asm/types.h`, `linux/bits.h`, `linux/typecheck.h`, `uapi/linux/kernel.h`, `asm-generic/bitops/generic-non-atomic.h`, and `asm/bitops.h`. Static assertions verify that architecture, constant, and generic bitop prototypes match. `bitmap.h`, request flags, queue flags, cgroup bitmaps, and pointer tagging helpers build on this API.

## Risks And Test Signals
Risks include using non-atomic `__*` bitops for shared state, invoking `__ffs64()` with zero, passing invalid sign-bit indexes, relying on pointer bit operations when alignment does not leave spare low bits, or breaking prototype parity between architecture and generic helpers. Test signals should cover constant folding, runtime bitops, 32-bit and 64-bit builds, rotate by zero and word-size multiples, compare/exchange retry behavior, and sparse/typecheck warnings.
