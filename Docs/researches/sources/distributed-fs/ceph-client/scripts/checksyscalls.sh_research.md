# sources/distributed-fs/ceph-client/scripts/checksyscalls.sh

## Purpose
`checksyscalls.sh` checks whether the current architecture exposes required Linux syscall numbers relative to the i386 syscall table, while suppressing known legacy, ABI-specific, MMU-specific, and replacement syscall cases.

## Important APIs, Types, and Functions
`ignore_list()` emits a C preprocessor fragment containing many `__IGNORE_*` macros gated by kernel config and ABI macros. `syscall_list()` reads `arch/x86/entry/syscalls/syscall_32.tbl`, sorts syscall rows numerically, and emits `#warning syscall NAME not implemented` guarded by `!defined(__NR_NAME)` and `!defined(__IGNORE_NAME)`.

## Control Flow and State
The script enables `set -e`, builds the reference table path relative to the script, concatenates generated ignore and syscall check fragments, and pipes them to the compiler command supplied as argv with `-Wno-error -Wno-unused-macros -E -x c -`. It optionally appends dependencies to `$DEPFILE` for fixdep integration. It has no persistent state.

## Dependencies and Integration
It depends on POSIX shell, `grep`, `sort`, and a C preprocessor compatible with kernel headers. The caller supplies the compiler and options, normally through Kbuild.

## Risks and Test Signals
The reference is i386-specific, so the ignore list is part of the contract and can go stale as syscalls evolve. Shell word splitting intentionally expands the compiler command but makes quoting sensitive. Test by running through representative Kbuild compile commands for 32-bit, 64-bit, MMU, no-MMU, and `DEPFILE` modes and checking that only expected warnings appear.
