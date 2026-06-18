# sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/errno.h

## Purpose
MIPS ABI-specific errno numbering table for tools.

## Important APIs, Types, and Functions
Includes generic base errnos and defines MIPS-specific values for IPC, STREAMS, networking, restart, filesystem, key, robust mutex, RF-kill, hardware poison, and quota errors. Aliases include `EFSBADCRC` to `EBADMSG`, `EFSCORRUPTED` to `EUCLEAN`, and `EWOULDBLOCK` to `EAGAIN`.

## Control Flow, State, and Persistence
No control flow; constants are compiled into callers that translate or compare errno values.

## Dependencies and Integration Points
Integrated with MIPS UAPI consumers and tools that must display or interpret target errno numbers rather than host numbers.

## Risks and Test Signals
Risk is ABI-sensitive numbering drift, especially because MIPS differs from generic Linux errno ordering. Test signals are errno-name lookup tests and target syscall trace decoding.
