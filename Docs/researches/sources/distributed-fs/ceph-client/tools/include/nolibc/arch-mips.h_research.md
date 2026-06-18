# sources/distributed-fs/ceph-client/tools/include/nolibc/arch-mips.h

## Purpose
Provides the nolibc architecture backend for MIPS. It is the register-level bridge between generic nolibc syscall wrappers and the Linux syscall ABI for this CPU family, and it also supplies the minimal process entry stub used when nolibc owns program startup.

## APIs, Types, and Functions
The core API surface is the macro family `__nolibc_syscall0()` through `__nolibc_syscall6()`, each binding syscall number and arguments to the ABI-mandated registers, executing the architecture trap instruction, and returning the raw kernel result. The file defines an entry symbol `__start` when `NOLIBC_NO_RUNTIME` is not set. It covers o32-style argument passing with `v0` syscall numbers, `a0`-`a3` plus stack arguments for five- and six-argument calls, error detection through `a3`, and ABI-specific stack reservation. MIPS uses `__start` rather than `_start`.

## Control Flow, State, and Persistence
Generic wrappers in `sys.h`, `fcntl.h`, `time.h`, and `sys/*.h` expand through these macros. The only runtime control flow here is inline assembly: move arguments, issue the trap, collect the return register, and branch from the entry stub into `_start_c()` with the initial stack pointer. No heap or persistent C state is owned by the header.

## Dependencies and Integration
Includes `compiler.h` for attributes and `crt.h` for `_start_c()`. It is selected by `arch.h` based on compiler predefined architecture macros and is consumed transitively by `nolibc.h` and all syscall wrapper headers.

## Risks and Test Signals
Risks are ABI register mistakes, incomplete clobber lists, stack alignment errors in the entry stub, and divergence between old and current syscall availability. Test signals are cross-architecture nolibc selftest builds, static inspection of generated syscall assembly, running simple `write`, `exit`, `fork` or `vfork`, `mmap`, and `select` tests under the target ABI, and building both runtime-owned and `NOLIBC_NO_RUNTIME` modes.
