# sources/distributed-fs/ceph-client/net/rds/af_rds.c

## Purpose
`af_rds.c` implements the AF_RDS socket family and module lifecycle for Reliable Datagram Sockets. It owns socket creation/destruction, socket options, connect/getname/poll/ioctl behavior, global socket accounting, and RDS info exports for sockets and queued receive messages.

## Important APIs, Types, And Functions
Main socket operations are `rds_release()`, `rds_getname()`, `rds_poll()`, `rds_ioctl()`, `rds_setsockopt()`, `rds_getsockopt()`, `rds_connect()`, and `rds_create()`. Lifecycle functions are `rds_init()` and `rds_exit()`. Helpers include `rds_wake_sk_sleep()`, option helpers for bools, congestion monitor, transport selection, receive timestamp, receive latency tracing, and socket info exporters for IPv4/IPv6.

## Control Flow
Module init seeds `rds_gen_num`, initializes bind/connections/threads/sysctl/stats/proto/socket registration, then registers info callbacks. Socket create requires `SOCK_SEQPACKET` and protocol 0, allocates `struct rds_sock`, initializes send/receive/notify/congestion/RDMA/zcopy queues and locks, and adds it to the global socket list.

Release orphans the socket, clears receive queue, removes congestion monitoring, unbinds, drops pending sends/RDMA keys/notifications/zerocopy completions, removes from global list, drops transport ref, clears `sock->sk`, and puts the sock. Poll reports readability for receive data, notifications, zerocopy completions, and congestion changes; writability is based on send-buffer accounting but not a guarantee that a destination is uncongested.

Socket options dispatch RDS-specific cancellation, memory region management, receive errors, congestion monitoring, transport selection, timestamping, and receive path latency tracing. Connect validates IPv4/IPv6 unicast destinations, records peer address/port, and handles IPv6 link-local scope consistency.

## State And Persistence
Global state includes `rds_sock_list`, `rds_sock_count`, `rds_poll_waitq`, and generated `rds_gen_num`. Per-socket state includes bound and connected addresses/ports/scope, selected transport, TOS, queues, congestion monitor fields, RDMA keys, and zcopy notification queues. State is in-memory only.

## Dependencies And Integration Points
This file integrates with `bind.c`, `cong.c`, `connection.c`, send/recv/RDMA/message/stat/sysctl/thread subsystems, transport registration, Linux proto/socket registration, and RDS info getsockopt.

## Risks
Release ordering is important because receive paths can race with close; `SOCK_DEAD`, receive locks, and queue clearing are relied on. Poll semantics are intentionally non-intuitive and apps may misinterpret EPOLLOUT. Transport selection is restricted for non-TCP transports outside `init_net`. TOS cannot be changed after a connection/transport is attached. IPv6 link-local scope must stay consistent across bind/connect.

## Test Signals
Coverage should include create type/protocol rejection, release while receives are queued, poll for congestion notifications and zcopy/errors, all socket option validation paths, transport selection before bind, non-init-net RDMA rejection, IPv4/IPv6 connect validation, getsockname/getpeername for unbound and connected sockets, and info export buffer sizing.
