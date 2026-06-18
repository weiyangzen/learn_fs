# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/include/platform/simcall-iss.h

Purpose: Defines native ISS host service numbers, select constants, argument query calls, and inline `simcall` ABI.

Important APIs, types, and functions: `SYS_*` constants for file, process, socket, select, ioctl, and argv services; `XTISS_SELECT_ONE_*`; static `errno`; and `__simc()`.

Control flow: `__simc()` places arguments in `a2`-`a5`, executes the `simcall` instruction, records errno from `a3`, and returns result from `a2`.

State and persistence: Updates translation-unit-local `errno` after every simcall.

Dependencies and integration: Included by `simcall.h` under `CONFIG_XTENSA_SIMCALL_ISS`; consumed by ISS setup, console, net, and simdisk code.

Risks: Host service numbers are simulator ABI, not Linux syscall numbers; static header `errno` is per C file; some service constants are documented as unavailable or not fully compatible.

Test signals: Native ISS boot, command-line argv import, file I/O, tuntap ioctl/poll if supported, and error propagation.
