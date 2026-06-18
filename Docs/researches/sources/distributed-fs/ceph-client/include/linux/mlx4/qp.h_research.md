# sources/distributed-fs/ceph-client/include/linux/mlx4/qp.h

## Purpose
Defines mlx4 queue-pair states, option masks, RSS context, QP path/context layout, WQE segment formats, QP update parameters, and QP lifecycle helpers.

## Important APIs/Types
Includes QP optional flags, states, service types, migration states, permission bits, RSS hash flags/context, `mlx4_qp_path`, `mlx4_qp_context`, `mlx4_update_qp_context`, update masks, WQE control flags, WQE segment structures for control/datagram/LSO/bind/FMR/local-inval/remote/atomic/data/inline operations, update-QP parameter structures, and APIs for lookup, update, modify, query, to-ready, remove, entropy, and put.

## Control Flow
QP setup reserves a QPN, fills a context, transitions RST->INIT->RTR->RTS, posts WQEs using these segment layouts, and handles completions/events. Runtime updates alter selected fields via masks.

## State And Persistence
State spans software `mlx4_qp`, radix-tree lookup, firmware QP context, doorbell records, MTT-backed queue rings, WQEs, refcounts, and completions.

## Dependencies And Integration Points
Depends on mlx4 device definitions and Ethernet constants. Integrates with RDMA verbs, mlx4_en RSS/Ethernet QPs, RoCE entropy, CQs/SRQs, firmware commands, and core lookup tables.

## Risks
State transition errors, endian/packing bugs, invalid update masks, RSS offset assumptions, QPN folding misuse, reserved LKey misuse, and teardown races.

## Test Signals
QP create/query/modify/to-ready/remove, RSS hashing, VLAN/source-check updates, WQE posting for all major opcodes, RoCE entropy, lookup/refcount behavior, and event-time teardown.
