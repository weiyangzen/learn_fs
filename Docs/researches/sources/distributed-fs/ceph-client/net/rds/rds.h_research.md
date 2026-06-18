# sources/distributed-fs/ceph-client/net/rds/rds.h

## Purpose
`rds.h` is the central private header for the RDS kernel implementation. It defines wire constants, core connection/socket/message/RDMA/statistics structures, transport callback contracts, inline helpers, and cross-file prototypes for the RDS core and transports.

## Important APIs, Types, and Functions
Major definitions include protocol constants (`RDS_PROTOCOL_*`, `RDS_PORT`), fragmentation and message limits (`RDS_FRAG_SIZE`, `RDS_MAX_MSG_SIZE`), congestion map sizing, connection states, connection flags, multipath constants, `struct rds_conn_path`, `struct rds_connection`, `struct rds_header`, extension header structs, `struct rds_incoming`, `struct rds_mr`, `struct rds_message`, `struct rds_notifier`, `struct rds_transport`, `struct rds_sock`, and `struct rds_statistics`.

Important inline helpers include RDMA cookie pack/unpack, `rds_message_zcopy_queue_init()`, socket/container conversions, send/receive buffer accounting, connection state tests/transitions, checksum make/verify, and `rds_destroy_pending()`. The header declares APIs implemented by bind, congestion, connection, message, page, recv, send, rdma, stats, sysctl, threads, and transport modules.

## Control Flow
The header shapes the entire RDS control flow. Sockets bind to `rds_sock` state, sends allocate `rds_message` objects, transports implement `struct rds_transport` callbacks for connection setup, transmit, RDMA, receive-copy, MR management, and stats, and received transport fragments eventually become `rds_incoming` objects queued on sockets. Connection paths carry per-path send queues, retransmit lists, state, work items, sequence counters, and transport-private data. Multipath-aware transports can use multiple `rds_conn_path` entries; `rds_single_path.h` maps older single-path code to path zero.

## State and Persistence
All structures are in-kernel volatile state. `rds_connection` persists per address pair, `rds_conn_path` persists per path, `rds_sock` persists per socket, `rds_message` and `rds_incoming` are refcounted per operation, and `rds_mr` persists while registered to a socket. No state is persisted to disk by this header.

## Dependencies and Integration Points
The header includes core networking, scatterlist, highmem, RDMA CM, mutex, rhashtable, refcount, IPv6, and `info.h`. It is included by almost every RDS source file and by transport-specific files. Its `struct rds_transport` is the primary integration contract between RDS core and loopback/TCP/IB transports.

## Risks
This header is ABI-adjacent for internal modules and wire-format-critical for `struct rds_header` and extension constants. Layout or semantic changes can break transport interoperability, user control-message behavior, or refcount ownership. The transport callback contract is broad; missing callback validation in callers can produce NULL dereferences. Many inline state helpers warn when used with multipath-capable transports incorrectly.

## Test Signals
Useful validation includes build coverage across IPv4/IPv6 and RDMA configs, protocol header checksum/extension packing tests, transport callback conformance tests, connection state transition stress, multipath handshake tests, socket receive/send queue lifetime tests, and RDMA MR lifetime tests.
