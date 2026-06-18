# sources/distributed-fs/ceph-client/tools/arch/parisc/include/uapi/asm/errno.h

## Purpose
PARISC ABI-specific errno numbering for tools.

## Important APIs, Types, and Functions
Includes generic errno base and defines PARISC-specific values for IPC, STREAMS, networking, restart, filesystem, key, robust mutex, and hardware poison cases. It keeps compatibility aliases such as `EWOULDBLOCK`, `EDEADLOCK`, `EFSBADCRC`, and `EFSCORRUPTED`.

## Control Flow, State, and Persistence
No flow or state; constants are consumed at compile time.

## Dependencies and Integration Points
Integrated with target errno display and syscall tracing for PARISC.

## Risks and Test Signals
Risk is target-host errno confusion because PARISC numbering differs from generic Linux. Test signals are errno mapping tests and syscall trace output checks.
