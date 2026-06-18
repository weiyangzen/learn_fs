# sources/distributed-fs/ceph-client/include/net/sctp/sctp.h

## Purpose
This is the base SCTP internal header. It gathers subsystem prototypes, global caches/sysctls, SNMP statistic macros, protocol registration hooks, socket helpers, packet receive/error paths, transport hash traversal, primitive entry points, IPv6 optional hooks, and inline utility functions.

## Important APIs, Types, And Functions
It declares protocol/socket APIs (`sctp_inet_connect()`, `sctp_backlog_rcv()`, `sctp_poll()`), primitive functions (`ASSOCIATE`, `SHUTDOWN`, `ABORT`, `SEND`, `ASCONF`, `RECONF`), input/error handlers, transport hash lookup/traversal, proc/offload/scheduler setup, stream reset calls, caches, sysctl arrays, MIB counters, debug object counters, sysctl registration, IPv6 registration stubs, association-id mapping, list helpers, skb ownership, parameter/error walkers, hash functions, socket/association state predicates, v4/v6 address mapping, PMTU helpers, PLPMTUD state helpers, and `sctp_sock_set_nodelay()`.

## Control Flow
Upper-layer socket operations call primitives, primitives enter the state machine, and commands drive output/input queues. Receive paths enter `sctp_rcv()` and error handlers locate endpoints/transports. Timers and PMTU helpers update transport state and can reschedule probe timers.

## State And Persistence
Persistent state is external: per-net stats, global caches, association idr, transport hash, sysctls, and object counters. Inline helpers update association stats and socket memory accounting.

## Dependencies And Integration Points
It integrates SCTP with inet protosw, sockets, procfs, SNMP, sysctl, IPv6, offload, stream schedulers, rhashtable transport lookup, and kernel memory accounting.

## Risks And Test Signals
Risks include hash-size power-of-two assumptions, skb receive accounting errors, PMTU underflow, address-family mapping mistakes, stale dst cache handling, and config-stub mismatches. Test signals include IPv4/IPv6 SCTP module load, connect/listen/send/recv, ICMP error handling, sysctl registration, SNMP counters, PMTU changes, and UDP encapsulation.
