# sources/distributed-fs/ceph-client/io_uring/epoll.h

## Purpose
This header declares io_uring epoll operation handlers when epoll support is compiled in.

## Important APIs, Types, And Functions
- `io_epoll_ctl_prep()` and `io_epoll_ctl()`.
- `io_epoll_wait_prep()` and `io_epoll_wait()`.

## Control Flow
No runtime flow is defined. Declarations are guarded by `CONFIG_EPOLL`.

## State And Persistence
No state is defined here.

## Dependencies And Integration Points
It connects epoll operation implementations to the io_uring opcode table in builds with epoll support.

## Risks And Edge Cases
Callers must not reference these prototypes without matching config guards in builds where `CONFIG_EPOLL` is off.

## Test Signals
Compile coverage with `CONFIG_EPOLL=y/n` and runtime epoll operation tests validate the header.
