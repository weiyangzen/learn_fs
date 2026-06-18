# sources/distributed-fs/ceph-client/arch/sparc/kernel/getsetcc.S

## Purpose
`getsetcc.S` implements sparc64 helpers for software traps that get or set integer condition codes in a saved `pt_regs` frame.

## Important APIs, Types, and Functions
The two global functions are `getcc` and `setcc`. Both accept a `struct pt_regs *` in `%o0` and use `PT_V9_TSTATE` plus `PT_V9_G1` offsets.

## Control Flow and State
`getcc()` loads saved TSTATE, shifts the ICC bits into the low nibble, masks them, and stores the result into saved `%g1`. `setcc()` loads saved TSTATE and saved `%g1`, clears the `TSTATE_ICC` field, masks the user-provided condition code bits, merges them into TSTATE, and stores the updated TSTATE.

## Persistence and Dependencies
Only the saved trap frame is mutated. The helpers depend on V9 TSTATE layout and `pt_regs` offsets matching assembly expectations.

## Integration Points, Risks, and Test Signals
These helpers integrate with user-visible get/set condition-code trap emulation. Risks are limited but include letting non-ICC TSTATE bits leak from user input or using stale offsets. Test signals include compatibility tests that execute getcc/setcc traps and verify only condition-code bits change.
