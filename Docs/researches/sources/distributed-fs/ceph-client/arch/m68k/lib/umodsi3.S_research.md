# sources/distributed-fs/ceph-client/arch/m68k/lib/umodsi3.S

## Purpose
Implements the exported `__umodsi3` unsigned 32-bit modulo helper for m68k kernels that rely on software arithmetic support.

## APIs, Flow, And State
The public symbol is `__umodsi3`, exported with `EXPORT_SYMBOL`. It reads dividend and divisor from the stack, calls `__udivsi3` to compute `a / b`, multiplies that quotient by the divisor, subtracts the product from the original dividend, and returns the remainder in `d0`. On non-ColdFire it calls `__mulsi3`; on ColdFire it uses native `mulsl`.

## Dependencies And Integration
Depends directly on `__udivsi3` and, for classic 680x0 builds, `__mulsi3`. The helper is built alongside the other libgcc arithmetic shims when the m68k CPU configuration lacks sufficient hardware arithmetic support. Compiler-generated unsigned modulo operations and other kernel code can bind to this exported symbol.

## Risks And Test Signals
Correctness inherits all division and multiplication edge cases, especially zero divisors and quotient overflow behavior. Stack offsets differ from `__udivsi3` because this routine pushes arguments for helper calls; regressions tend to show as widespread bad `%` results. Test signals include m68k arithmetic boot smoke tests and paired identities such as `a == (a / b) * b + (a % b)` for nonzero `b`.
