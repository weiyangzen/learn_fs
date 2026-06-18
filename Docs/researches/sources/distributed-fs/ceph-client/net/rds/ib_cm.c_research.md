# sources/distributed-fs/ceph-client/net/rds/ib_cm.c

## Purpose
`ib_cm.c` implements RDS/IB RDMA connection management. It negotiates protocol and flow control, creates/destroys QPs/CQs/DMA header resources, handles CM connect/accept paths, polls completion queues via tasklets, and allocates/frees per-connection IB state.

## Important APIs, Types, And Functions
Important APIs are `rds_ib_cm_connect_complete()`, `rds_ib_cm_handle_connect()`, `rds_ib_cm_initiate_connect()`, `rds_ib_conn_path_connect()`, `rds_ib_conn_path_shutdown()`, `rds_ib_conn_alloc()`, `rds_ib_conn_free()`, and `__rds_ib_conn_error()`. Major helpers include `rds_ib_set_protocol()`, `rds_ib_set_flow_control()`, `rds_ib_cm_fill_conn_param()`, CQ handlers/tasklets, DMA header alloc/free helpers, `rds_ib_setup_qp()`, and `rds_ib_protocol_compatible()`.

## Control Flow
Outgoing connect creates an RDMA CM id, binds source/destination sockaddr from RDS addresses, resolves address, sets proposed protocol/flow control, sets up QP resources, fills private data, and calls `rdma_connect_locked()`. Incoming connect validates protocol private data, extracts IPv4/IPv6 addresses and TOS, finds link-local interface if needed, creates or finds an RDS connection, transitions it to CONNECTING, attaches the CM id, sets up QP resources, fills response private data, and accepts.

QP setup obtains an `rds_ib_device`, adds the connection to the device, sizes send/recv rings, creates send/recv CQs with balanced completion vectors, requests notifications, creates an RC QP, allocates DMA-mapped send/recv header arrays and ACK header, allocates send/recv work arrays, and initializes ACK state. Completion handlers schedule send/recv tasklets. Tasklets poll CQs, dispatch send/MR/recv completions, update ACK state, drop acked messages, attempt ACK sends, and resume RDS send xmit when appropriate.

Connect complete parses peer private data, sets negotiated protocol and flow control, rejects unsupported old versions, initializes rings, refills receives, updates IB device IP address, processes piggyback ACK, and calls `rds_connect_complete()`. Shutdown disconnects RDMA CM, flushes MRs, waits for receive ring/signaled sends/fastreg state to drain, kills tasklets, quiesces CQs, destroys QP/CQs, frees DMA headers/work arrays, removes the connection from the device, resets ACK/flow-control/ring state, and frees partial incoming state.

## State And Persistence
Per-connection state includes CM id, PD, CQs, tasklets, send/recv rings, DMA headers, ACK header, credits, flow-control flag, active/passive role, CQ quiesce flag, vector indexes, and work arrays. Nodev/device lists are maintained through `rds_ib_conn_alloc()` and device add/remove helpers.

## Dependencies And Integration Points
The file integrates with RDMA CM, IB verbs, RDS core connection state machine, send/recv/MR handlers, MR flushing, sysctl flow-control settings, device management in `ib.c`, and protocol definitions in `ib.h`.

## Risks
Setup and teardown are highly staged; every failure path must free only resources already initialized and balance vector/device refs. Private data parsing handles legacy/zeroed RDMA CM buffers and unaligned ACK sequence loads. Shutdown waits can deadlock if completions or fastreg counters are lost. Incoming/outgoing connect races intentionally drop or wait on existing connections. The code currently reports only single-path assumptions in several places despite broader RDS multipath support.

## Test Signals
Tests should cover protocol compatibility negotiation, IPv4/IPv6 private data, link-local ifindex lookup, incoming race states, QP setup failure at each allocation step, CQ vector balance/unbalance, send/recv CQ polling, MR completion dispatch, connect complete with piggyback ACK, shutdown after partial setup, shutdown with in-flight FRMRs, and active/passive loopback cases.
