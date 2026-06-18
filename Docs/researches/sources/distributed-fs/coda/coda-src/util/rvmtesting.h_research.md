# sources/distributed-fs/coda/coda-src/util/rvmtesting.h

## Purpose
Declares optional RVM memory-write debugging hooks.

## Important APIs, Types, And Functions
The header declares `protect_page`, `unprotect_page`, and `my_sigBus`.

## Control Flow
Debug builds install/use these functions to protect memory and handle SIGBUS diagnostics.

## State And Persistence
No state is declared here; implementation state is debug-only and process-local.

## Dependencies And Integration Points
Requires platform definitions for `struct sigcontext`. Intended for conditional `RVMTESTING` builds.

## Risks
The closing `#endif _RVMTESTING_H` is nonstandard trailing token style. Declarations may be unavailable or incompatible on modern systems.

## Test Signals
Compile with and without `RVMTESTING` on supported platforms and verify signal-handler signature compatibility.
