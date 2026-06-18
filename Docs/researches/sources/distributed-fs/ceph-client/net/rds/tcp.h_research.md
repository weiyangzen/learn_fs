# sources/distributed-fs/ceph-client/net/rds/tcp.h

## Purpose
Declares the private interface and state shared by the RDS TCP transport implementation files.

## Important APIs, Types, and Functions
Defines `RDS_TCP_PORT` as 16385, `struct rds_tcp_net`, `struct rds_tcp_incoming`, `struct rds_tcp_connection`, and `struct rds_tcp_statistics`. It declares transport entry points from `tcp.c`, `tcp_connect.c`, `tcp_listen.c`, `tcp_recv.c`, `tcp_send.c`, and `tcp_stats.c`, plus the `rds_tcp_stats_inc()` wrapper over the generic per-CPU stats helper.

## Control Flow
The header has no executable control flow, but it encodes module boundaries: connection allocation attaches a `struct rds_tcp_connection` to every `rds_conn_path`, receive code fills `struct rds_tcp_incoming`, pernet code owns `struct rds_tcp_net`, and send/listen/connect files call across the declared interfaces.

## State and Persistence
Structures define runtime-only state: accept serialization, listener and accepted sockets, sysctl values, partial incoming header/data tracking, original TCP callbacks, active socket info fields, client source-port group, and receive-drain waitqueue.

## Dependencies and Integration
Depends on RDS core types, kernel sockets, skb queues, work structs, wait queues, and sysctl types. This header is the integration contract that keeps the TCP transport split across smaller compilation units.

## Risks and Test Signals
Risks include stale prototypes after implementation changes and fields whose ownership is split across callback, workqueue, and teardown paths. Test signals are clean compile coverage for all TCP transport files, CFI/prototype consistency, and behavior that exercises each declared callback path.
