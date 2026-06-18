# sources/distributed-fs/orangefs/src/io/bmi/bmi_tcp/sockio.h

## Purpose

This header exposes the TCP socket utility API used by `bmi-tcp.c` and defines convenience macros for socket options and blocking-mode changes.

## Important APIs, Types, And Macros

- Function prototypes cover socket creation, bind, specific bind, connect, address initialization, nonblocking recv/send/peek/vector I/O, socket option access, and optional sendfile.
- `GET_RECVBUFSIZE`, `GET_SENDBUFSIZE`, `SET_RECVBUFSIZE`, and `SET_SENDBUFSIZE` wrap `SO_RCVBUF` and `SO_SNDBUF`.
- `GET_MINSENDSIZE`, `GET_MINRECVSIZE`, `SET_MINSENDSIZE`, and `SET_MINRECVSIZE` wrap low-watermark options.
- `BRAINDEADSOCKS` disables buffer-size setters for platforms where changing socket buffers is unsafe.
- `SET_NONBLOCK`, `SET_NONBLOCK_AND_SIGIO`, and `CLR_NONBLOCK` use `fcntl` to manipulate fd flags.

## Control Flow

The header itself has no runtime control flow beyond macros. The nonblocking macros read current flags and write modified flags. The socket option macros route calls through the implementation in `sockio.c`.

## State And Persistence Behavior

The macros mutate kernel fd flags and socket options. No process-local state is stored by the header.

## Dependencies And Integration Points

The header depends on socket and networking system headers plus `bmi-types.h`. It is included by `bmi-tcp.c` and `sockio.c`. Its macros provide the names used by `bmi_set_sock_buffers` and setup paths in the transport.

## Risks And Edge Cases

- `SET_NONBLOCK` and related macros do not check `fcntl` failures and call `fcntl(F_GETFL)` inside `F_SETFL` arguments.
- `CLR_NONBLOCK` can clobber flag updates made concurrently by other code on the same fd.
- Buffer-size setter macros become empty statements under `BRAINDEADSOCKS`, so callers expecting return values must not rely on them.
- The header declares `struct iovec` use but does not include `<sys/uio.h>` directly; it relies on include order from consumers.

## Test Signals

Tests should compile consumers with strict warnings, verify macro expansion under `BRAINDEADSOCKS`, exercise nonblocking flag transitions, and confirm socket buffer macros route to the implementation wrappers.
