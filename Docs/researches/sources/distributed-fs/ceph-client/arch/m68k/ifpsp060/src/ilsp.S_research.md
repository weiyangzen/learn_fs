# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/src/ilsp.S

## Purpose
`ilsp.S` is the library-facing integer support package for 68060 instructions that need software emulation when used as callable routines rather than as exception handlers. It provides branch-table entry points for signed and unsigned 64-bit divide, signed and unsigned 32x32-to-64 multiply, and `cmp2` byte/word/long comparisons against address or data register values. Unlike `isp.S`, this file does not decode trapped instruction frames; callers pass operands and output pointers on the stack.

## Important APIs, Types, And Functions
The leading branch table exports `_060LSP__idivs64_`, `_060LSP__idivu64_`, `_060LSP__imuls64_`, `_060LSP__imulu64_`, and six `cmp2` routines: `_060LSP__cmp2_Ab_`, `_060LSP__cmp2_Aw_`, `_060LSP__cmp2_Al_`, `_060LSP__cmp2_Db_`, `_060LSP__cmp2_Dw_`, and `_060LSP__cmp2_Dl_`. The 64-bit divide API takes divisor, high dividend, low dividend, and a pointer to a two-longword result area where remainder is stored first and quotient second. The multiply API takes multiplier, multiplicand, and a pointer to a two-longword result area. The `cmp2` API takes `Rn` and a pointer to the lower/upper bound pair.

The divide implementation uses local frame slots `POSNEG`, `NDIVISOR`, `NDIVIDEND`, `DDSECOND`, `DDNORMAL`, `DDQUOTIENT`, and `DIV64_CC`. The multiply routines use `MUL64_CC`; the compare routines use `CMP2_CC`. Internal helpers `ldclassical`, `lddknuth`, and `ldmm2` implement Knuth Algorithm D and 32x32-to-64 multiplication for long division.

## Control Flow
Both divide entry points save `%d2` through `%d7`, preserve incoming condition-code state in `DIV64_CC`, mark signed versus unsigned in `POSNEG`, then share `ldiv64_cont`. The shared path loads the divisor, forces a real divide-by-zero trap with `divu.w &0,%d0` if needed, normalizes signed operands by recording signs and converting to unsigned, handles fast zero and 32-bit divide cases, rejects quotient overflow, and otherwise calls `ldclassical`. Signed division post-processing applies the original dividend sign to the remainder and the XOR of dividend/divisor signs to the quotient, with explicit signed overflow checks for `0x80000000`.

`ldclassical` has a fast path for word-sized divisors and a full Knuth Algorithm D path for long divisors. The full path normalizes the divisor/dividend until the high divisor bit is set, estimates two quotient words, adjusts overestimates by multiplying back with `ldmm2`, subtracts, optionally adds the divisor back, then denormalizes the remainder.

The multiply routines load operands, special-case zero, convert signed inputs to positive values when needed, compute four 16x16 partial products, combine carries into high and low longwords, optionally two's-complement the 64-bit result, set `N` or `Z` while preserving incoming `X`, and store the two-longword result through the caller's pointer. The `cmp2` routines sign-extend bounds and, for data-register variants, the register operand. `l_cmp2_cmp` computes the two comparisons specified by `cmp2`, merges the new `Z`/`N` bits with preserved old `X`/`N`/`V`, writes `%cc`, restores saved registers, and returns.

## State And Persistence
State is entirely transient: stack frames, caller-provided result buffers, condition codes, and scratch registers. The routines save/restore their documented scratch register sets and no FP registers. Divide-by-zero is intentionally persistent only as an architectural exception side effect: the library routine saves unchanged dividend values before forcing the hardware divide-by-zero exception so the OS can observe the fault.

## Dependencies And Integration Points
This code requires 68020+ style instructions used by the Motorola package, including `link.w`, `movm.l`, `tdivu.l`, `divu.w`, `mulu.w`, `addx`, `negx`, and `rtd`-compatible caller environments. It is integrated by the branch table at file top, with a 0x200 alignment gap reserved for future entries. It is standalone relative to `isp.S`; there are no external symbol dependencies beyond the caller and the processor exception environment for the divide-by-zero case.

## Risks
The APIs are assembly calling-convention sensitive: stack offsets must match exactly, result pointers must be valid and aligned enough for longword stores, and callers must tolerate condition-code changes. Divide and multiply both preserve only selected condition-code bits by design; code that expects exact hardware instruction side effects beyond those bits can diverge. The signed divide overflow boundaries are subtle, especially quotient `0x80000000`. The final result store order intentionally handles equal quotient/remainder or high/low destination cases; changing it can break compatibility. The forced divide-by-zero trap may not point at the original caller instruction, as the header explicitly warns.

## Test Signals
Strong tests compare quotient/remainder and condition codes for zero dividend, zero divisor, 32-bit fast path, long Knuth path, unsigned overflow, signed positive/negative combinations, and signed minimum-value boundaries. Multiply tests should cover zero, high-bit unsigned results, negative signed results, carry propagation across partial products, and equal-result-register semantics via the result buffer order. `cmp2` tests should check byte/word/long bounds, data versus address register sign extension, in-range equal-bound cases, and preservation of old `X`/`V` bits.
