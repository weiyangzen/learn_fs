# sources/distributed-fs/ceph-client/arch/arm/lib/div64.S

Purpose: implements `__do_div64`, an optimized nonstandard ABI helper for 64-bit dividend divided by 32-bit divisor used by ARM `do_div`.

Control flow handles divisor 0/1 and power-of-two fast paths, computes upper quotient bits when needed, then shifts remainder bits through a lower quotient loop. Division by zero calls `__div0` and returns zeroed outputs. State is only register state: quotient in `yh:yl` and remainder in `xh`. Dependencies include ARM endian register aliases, CLZ availability on ARMv5+, and `__div0` diagnostics. Risks are nonstandard calling convention misuse, divide-by-zero behavior, and edge cases where upper quotient is required. Test signals include arithmetic selftests comparing `do_div` against compiler/runtime division for random 64/32 pairs.
