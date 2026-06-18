# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/uio.h

## Purpose
Provides vectored I/O wrappers for nolibc.

## APIs, Types, and Functions
Includes Linux UIO definitions and defines `_sys_readv`/`readv` and `_sys_writev`/`writev`.

## Control Flow, State, and Persistence
Wrappers pass fd, iovec array, and count to the kernel and return byte counts through `__sysret`. State is in caller buffers and fd offsets updated by the kernel.

## Dependencies and Integration
Depends on `../sys.h`, `../types.h`, and Linux `struct iovec`. It integrates with stdio alternatives and protocols that naturally scatter/gather buffers.

## Risks and Test Signals
Risks include invalid iovec pointers, count overflow, partial reads/writes, and fd offset side effects. Test signals are pipe/file readv-writev round trips, partial write handling, invalid iovec errors, and large count rejection.
