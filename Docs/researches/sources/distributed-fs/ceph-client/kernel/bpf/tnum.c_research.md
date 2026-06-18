# sources/distributed-fs/ceph-client/kernel/bpf/tnum.c

## Purpose

`tnum.c` implements tracked-number arithmetic used by the BPF verifier to represent partially-known integer values. A `struct tnum` stores known bits in `value` and unknown bits in `mask`; operations return conservative tnums that cover every concrete result possible from the operands.

## Important APIs, Types, And Functions

- Constructors: `tnum_const()`, `tnum_range()`, and global `tnum_unknown`.
- Bit shifts and arithmetic: `tnum_lshift()`, `tnum_rshift()`, `tnum_arshift()`, `tnum_add()`, `tnum_sub()`, `tnum_neg()`, and `tnum_mul()`.
- Bitwise operations: `tnum_and()`, `tnum_or()`, `tnum_xor()`, `tnum_bswap16()`, `tnum_bswap32()`, and `tnum_bswap64()`.
- Set-like operations: `tnum_overlap()`, `tnum_intersect()`, `tnum_union()`, `tnum_in()`, and `tnum_step()`.
- Size/subregister helpers: `tnum_cast()`, `tnum_subreg()`, `tnum_clear_subreg()`, `tnum_with_subreg()`, and `tnum_const_subreg()`.
- Diagnostics and constraints: `tnum_is_aligned()` and `tnum_sbin()`.

## Control Flow

Most operations are pure functions that combine input `value` and `mask` bit patterns. Arithmetic uses carry/borrow-aware formulas to expand uncertainty when unknown input bits can affect known output bits. Multiplication performs long multiplication over the uncertain multiplier, unioning accumulator states when a multiplier bit is unknown. `tnum_range()` computes a common prefix and unknown suffix covering a min/max interval.

`tnum_step()` is a compact enumeration helper: given a tnum and a current value `z`, it returns the smallest concrete member of the tnum greater than `z`, clamping to min or max when outside the range. It increments within the tnum mask by filling non-mask positions to propagate carry through gaps.

## State And Persistence Behavior

There is no mutable persistent state. All functions operate by value and return a new `struct tnum`. The only global is the immutable all-unknown `tnum_unknown`.

## Dependencies And Integration Points

The file depends on `linux/tnum.h`, basic kernel bit helpers such as `fls64()`, and byte-swap helpers. The primary integration point is verifier scalar range/value tracking; tnums are used to reason about pointer offsets, register values, alignment, subregister writes, and safety constraints.

## Risks And Edge Cases

Correctness requires over-approximation. Under-approximating any operation can make the verifier accept unsafe programs; excessive over-approximation can reject valid programs. Important edge cases include full-width ranges where `1ULL << 64` would be undefined, arithmetic right shifts with 32-bit versus 64-bit signed interpretation, multiplication with unknown bits, casts where `size * 8` reaches the supported width, and `tnum_step()` carry behavior when `d & ~mask` is zero or high-bit-sensitive.

## Test Signals

Useful tests include verifier selftests for scalar arithmetic, subregister behavior, alignment, bounds propagation, and branch pruning. Unit-style tests should compare tnum operation results against exhaustive concrete sets for small bit widths, check range extremes including `0..U64_MAX`, validate byte swaps and casts, and verify `tnum_step()` enumerates members monotonically without skipping valid values.
