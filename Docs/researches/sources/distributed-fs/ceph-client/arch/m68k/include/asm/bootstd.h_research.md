<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bootstd.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/bootstd.h

## Purpose
This header defines a uClinux/m68k bootloader system-call interface using `trap #2`. It provides syscall numbers and C wrapper-generating macros for bootloader operations such as reset, exec, file I/O, flash programming, environment access, and memory mapping.

## Important APIs, Types, And Functions
- `__BN_*` constants define bootloader call numbers up to `NR_BSC`.
- `__bsc_return()` converts negative bootloader errors in the `[-64, -1]` range into `errno` and `-1`.
- `_bsc0()` through `_bsc5()` generate wrappers with zero to five arguments passed in `%d1` through `%d5`, call number/result in `%d0`, and `trap #2`.

## Control Flow
Generated wrappers load registers, execute `trap #2`, then pass the result through `__bsc_return()`. Control transfers to bootloader firmware and returns with a result or error code.

## State And Persistence Behavior
The header owns no kernel state. Firmware calls may mutate bootloader environment variables, flash contents, file descriptors, mappings, or system reset state.

## Dependencies And Integration Points
It expects C library-style `errno` availability and m68k register calling conventions. It integrates with bootloader-aware standalone or early uClinux code.

## Risks And Edge Cases
Register constraints and return conversion are ABI-sensitive. Flash erase/write and reset calls are destructive. `__BN_setbenv` is commented as "get" but named set, so callers should verify bootloader ABI documentation.

## Test Signals
Bootloader interface tests for `_bsc*` argument passing, file open/read/write/close, environment get/set, flash range operations on safe targets, and error-to-errno conversion validate the macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/bootstd.h -->
