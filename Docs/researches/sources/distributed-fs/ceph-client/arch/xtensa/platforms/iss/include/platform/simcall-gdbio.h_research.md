# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/simcall-gdbio.h

Purpose: Defines simulator host service numbers and inline call ABI for GDBIO-backed ISS simcalls.

Important APIs, types, and functions: `SYS_open`, `SYS_close`, `SYS_read`, `SYS_write`, `SYS_lseek`, static `errno`, and `__simc()`.

Control flow: `__simc()` loads arguments into specific Xtensa registers (`a2`, `a6`, `a3`, `a4`), executes `break 1, 14`, captures return and errno registers, stores errno, and returns the host result.

State and persistence: Updates a header-local static `errno` variable in each translation unit including it.

Dependencies and integration: Selected by `CONFIG_XTENSA_SIMCALL_GDBIO` through `simcall.h`; used by ISS console/network/simdisk/setup wrappers.

Risks: Register ABI differs from ISS native `simcall`; static header `errno` has translation-unit scope, which is acceptable for simple simulator drivers but not a global libc-style errno; only a small syscall set is defined.

Test signals: GDBIO ISS boot, host open/read/write/lseek/close behavior, and errno reporting on failed host operations.
