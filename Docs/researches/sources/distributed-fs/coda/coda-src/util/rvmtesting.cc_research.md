# sources/distributed-fs/coda/coda-src/util/rvmtesting.cc

## Purpose
Contains optional `RVMTESTING` instrumentation for debugging writes to protected memory on old Mach/MIPS environments.

## Important APIs, Types, And Functions
When compiled with `RVMTESTING`, it defines `ClobberAddress`, `protect_page()`, `unprotect_page()`, `GPR()`, instruction decoding helper `getNextPc()`, `StoreInLoadDelay`, and signal handler `my_sigBus()`.

## Control Flow
Pages are protected with Mach `vm_protect`. On SIGBUS, `my_sigBus()` decodes the current or delay-slot instruction, determines whether a store targets `ClobberAddress`, zombies on illegal or targeted writes, otherwise temporarily unprotects the target, emulates simple byte/halfword/word stores, reprotects, and advances the saved PC through branch/jump decoding.

## State And Persistence
Debug-only global state includes `ClobberAddress`, `savedInstruction`, and debug level. It has no durable persistence and is compiled out unless `RVMTESTING` is defined.

## Dependencies And Integration Points
Depends on Mach VM APIs, MIPS instruction formats, `struct sigcontext`, `zombie()`, and Coda logging. It is historical diagnostic support for RVM corruption hunts.

## Risks
The code is architecture- and OS-specific, uses old-style casts and integer pointer truncation, and does not emulate `swl/swr`. The header exposes functions even when the implementation may compile to nothing. Modern platforms are unlikely to build this path.

## Test Signals
Only test on the intended Mach/MIPS configuration: protect/unprotect a page, trigger non-target and target stores, branch delay-slot handling, unaligned store handling, and build exclusion when `RVMTESTING` is unset.
