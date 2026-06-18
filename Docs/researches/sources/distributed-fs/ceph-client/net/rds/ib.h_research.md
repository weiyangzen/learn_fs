# sources/distributed-fs/ceph-client/net/rds/ib.h

## Purpose
`ib.h` is the central private header for RDS/IB. It defines protocol constants, connection-private negotiation formats, send/receive work descriptors, rings, ack state, IB connection/device structures, statistics, inline DMA sync wrappers, and cross-file function prototypes.

## Important APIs, Types, And Functions
Key types include `struct rds_ib_connection`, `struct rds_ib_device`, `struct rds_ib_send_work`, `struct rds_ib_recv_work`, `struct rds_ib_work_ring`, `struct rds_ib_ack_state`, `struct rds_ib_refill_cache`, `union rds_ib_conn_priv`, `struct rds_ib_conn_priv_cmn`, and `struct rds_ib_statistics`. Important constants define default WR counts, supported protocols, SGE counts, ACK WR id, credit bit packing, and MR pool ids. The header declares transport, CM, RDMA, recv, ring, send, stats, and sysctl functions.

## Control Flow
This header does not execute control flow, but it encodes the data contracts used by `ib.c`, `ib_cm.c`, `ib_recv.c`, `ib_send.c`, `ib_ring.c`, `ib_rdma.c`, and `ib_frmr.c`. Connection setup fills private data structures, send/recv paths consume work descriptors/rings, completion handlers update ack and credit fields, and MR operations use connection/device fields.

## State And Persistence
The structures describe persistent in-memory RDS/IB runtime state: CM ids, PDs, CQs, work rings, DMA header arrays, tasklets, ack flags, credits, MR pools, device limits, connection lists, vector load, and statistics. None is disk-persistent.

## Dependencies And Integration Points
The header depends on RDMA verbs, RDMA CM, PCI/slab primitives, RDS core headers, and RDMA transport definitions. It is the integration point for all RDS/IB implementation files.

## Risks
ABI-sensitive private connection data warns that fields must be appended rather than reordered. Credit packing assumes `atomic_t` is at least 32 bits. The fallback DMA sync macros shadow missing IB APIs. Structure fields are used across interrupt/tasklet/workqueue/process contexts, so lock and lifetime assumptions are spread across files.

## Test Signals
Validation is compile- and integration-heavy: protocol negotiation structure sizes for IPv4/IPv6, credit packing/unpacking, ring sizing, stats layout, ODP/MR pool fields, and cross-file prototype consistency.
