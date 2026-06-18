# sources/distributed-fs/ceph-client/arch/mips/lib/uncached.c

Purpose: runs a function through an uncached virtual mapping of both function address and stack.

Important APIs/functions: `run_uncached(void *func)`.

Control flow: reads current stack pointer, maps stack and target function from CKSEG0/CKSEG1 to CKSEG1 or from XKPHYS to uncached XKPHYS on 64-bit, BUGs on unsupported address ranges, then switches `$sp`, `jalr`s to the uncached function, restores `$sp`, and returns `$2`.

State and persistence: temporarily changes the CPU stack pointer during the call; no global state.

Dependencies and integration: used by cache/MMU-sensitive code that must execute uncached; depends on MIPS address-space macros.

Risks: only works for simple functions without stack arguments or complex return values. Unsupported addresses trigger `BUG()`. Caller must ensure cache coherency and interrupt expectations.

Test signals: platform cache init paths using `run_uncached`, 32/64-bit address mapping tests, and no stack corruption after return.
