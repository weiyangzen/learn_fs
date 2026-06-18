<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/div64.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/div64.h

## Purpose
This header implements `do_div()` for m68k CPUs with 64-bit-capable divide instructions and falls back to generic code for CPUs without required multiply/divide support.

## Important APIs, Types, And Functions
- Includes `<asm-generic/div64.h>` when `CONFIG_CPU_HAS_NO_MULDIV64` is set.
- Architecture `do_div(n, base)` divides a 64-bit value by a 32-bit base, stores the quotient back in `n`, and returns the remainder.
- The implementation uses `divul.l` and `divu.l` over the upper and lower 32-bit words.
- Defines `__div64_32` to suppress unused generic helper construction.

## Control Flow
The macro splits `n` into two 32-bit words, divides the upper word if nonzero, then divides the lower word with the carried remainder. The quotient words are reassembled into `n`.

## State And Persistence Behavior
Only the caller's `n` lvalue is updated. There is no persistent state.

## Dependencies And Integration Points
It depends on m68k divide instruction availability and Linux integer types. It is used throughout kernel code needing 64/32 division.

## Risks And Edge Cases
`do_div` evaluates and writes its first argument as a macro lvalue. Division by zero remains caller-invalid. Endianness of the union word order must match m68k big-endian layout.

## Test Signals
64-bit division unit tests across small/large dividends, upper-word nonzero cases, remainder validation, and builds for generic fallback configs validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/div64.h -->
