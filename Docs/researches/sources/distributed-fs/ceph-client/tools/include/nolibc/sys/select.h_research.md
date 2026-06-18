# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/select.h

## Purpose
Implements `select` and fd-set manipulation for nolibc.

## APIs, Types, and Functions
Defines `fd_set` plus `FD_ZERO`, `FD_SET`, `FD_CLR`, `FD_ISSET`, private `_sys_select`, and public `select`.

## Control Flow, State, and Persistence
Fd-set macros mutate caller-provided bitsets. `select` chooses the old `select` syscall on architectures that request it or uses `pselect6`/modern alternatives where available, then writes readiness bits and timeout state as the kernel dictates.

## Dependencies and Integration
Depends on `../types.h`, `../sys.h`, and architecture `__ARCH_WANT_SYS_OLD_SELECT` declarations. It integrates with event loops and `poll` alternatives in tiny tools.

## Risks and Test Signals
Risks include `FD_SETSIZE` assumptions, nfds exceeding the local bitset, timeout mutation differences, and old-select ABI packing. Test signals are pipe readiness, timeout-only selects, invalid fd errors, and arch coverage for both old and modern syscall paths.
