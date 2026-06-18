<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tnum.h -->
# sources/distributed-fs/ceph-client/include/linux/tnum.h

## Purpose
declares tristate-number operations used primarily by the eBPF verifier to represent known and unknown bits of scalar values.

## Important APIs, Types, and Functions
The file is 138 lines and exports these visible symbol families: types/enums `tnum`; macros/constants none; function-like macros none; inline helpers `tnum_is_const`, `tnum_equals_const`, `tnum_is_unknown`, `tnum_subreg_is_const`; external prototypes `tnum_const`, `tnum_range`, `tnum_lshift`, `tnum_rshift`, `tnum_arshift`, `tnum_add`, `tnum_sub`, `tnum_neg`, `tnum_and`, `tnum_or`, `tnum_xor`, `tnum_mul`, `tnum_overlap`, `tnum_intersect`, and 13 more.

## Control Flow
Verifier code constructs constants, unknowns, and ranges; propagates uncertainty through shifts, arithmetic, bitwise ops, multiplication, casts, byte swaps, and subregister updates; then tests alignment, subset inclusion, overlap, and formatting for diagnostics.

## State and Persistence Behavior
A `struct tnum` is immutable value/mask data passed by value. No global state is held except the exported `tnum_unknown` constant.

## Dependencies and Integration Points
It depends on integer types and integrates with BPF register range/var_off tracking, verifier logs, and alignment checks. Direct includes are `linux/types.h`.

## Risks and Edge Cases
Tnum ranges are conservative supersets; callers must not treat `tnum_range()` as an exact interval. Incorrect arithmetic propagation can make the verifier unsound or reject valid programs.

## Test Signals
Run BPF verifier selftests, unit-test each tnum operation, check range/subset edge cases, subregister propagation, byte swaps, alignment, and diagnostic formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tnum.h -->
