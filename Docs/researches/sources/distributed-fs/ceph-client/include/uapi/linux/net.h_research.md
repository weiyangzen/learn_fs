# sources/distributed-fs/ceph-client/include/uapi/linux/net.h

## Purpose
Defines legacy networking syscall multiplexor operation numbers, socket state enum, protocol count alias, and accept-state bit.

## Important APIs, Types, And Functions
Exports `NPROTO`, `SYS_SOCKET` through `SYS_SENDMMSG`, `socket_state`, and `__SO_ACCEPTCON`.

## Control Flow
Historically, architectures with `socketcall` used `SYS_*` operation numbers to dispatch individual socket operations. `socket_state` describes socket connection lifecycle states used in user-visible headers.

## State, Persistence, And Dependencies
Socket state persists in kernel socket objects. Depends on `linux/socket.h` and `asm/socket.h`.

## Integration Points
Used by libc compatibility layers, tracing, seccomp filters, and old architecture socketcall paths.

## Risks
This is a compatibility header; modern direct syscalls may not use `SYS_*`. `SS_*` names can conflict with userspace expectations if mixed with other socket state definitions.

## Test Signals
Validate socketcall numbering on applicable architectures, seccomp filter constants, socket state value stability, and `NPROTO == AF_MAX`.
