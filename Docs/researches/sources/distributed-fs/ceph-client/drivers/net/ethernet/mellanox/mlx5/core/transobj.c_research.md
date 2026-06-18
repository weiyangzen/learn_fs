# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/transobj.c

## Purpose
This file wraps mlx5 firmware commands for transport-domain and transport object lifecycle, and implements hairpin queue pairing between a function device and peer device. It is a general mlx5 core support file used by Ethernet/RDMA paths, not specific to SW steering.

## Important APIs, Types, And Functions
Exported transport command wrappers include allocation/deallocation of transport domains, create/modify/destroy/query RQ, create/modify/destroy/query SQ, query SQ state, create/modify/destroy TIR, create/modify/destroy TIS, create/modify/destroy RQT. Hairpin APIs are `mlx5_core_hairpin_create()`, `mlx5_core_hairpin_destroy()`, and `mlx5_core_hairpin_clear_dead_peer()`.

Internal hairpin helpers create RQs on the function device and SQs on the peer, transition SQs/RQs from reset to ready with peer VHCA and queue numbers, undo transitions on failures, and destroy queues.

## Control Flow
The simple wrappers set the opcode and object number fields, execute the corresponding command, and return object IDs from output buffers. `mlx5_core_query_sq_state()` allocates a query buffer, calls SQ query, reads the state from SQ context, and frees the buffer.

Hairpin creation allocates one object containing arrays of RQNs and SQNs, creates all function RQs, creates all peer SQs, pairs peer SQs first, then function RQs. On failures it rolls back modified queues and destroys created queues. Destroy unpairs, destroys queues, and frees memory. Dead-peer cleanup unpairs/destroys peer SQs and marks `peer_gone` so later destroy skips peer SQ destruction.

## State And Persistence
Firmware object IDs persist in device hardware until destroyed: transport domain numbers, RQNs, SQNs, TIRNs, TISNs, and RQTNs. Hairpin state persists in `struct mlx5_hairpin`, which stores devices, channel count, dynamic RQN/SQN arrays, and `peer_gone`.

## Dependencies And Integration Points
The file depends on `linux/mlx5/driver.h`, `linux/mlx5/transobj.h`, command layout macros, and `mlx5_cmd_exec*` helpers. Ethernet TC hairpin code calls `mlx5_core_hairpin_create()`, and other core/driver paths call the exported transport object wrappers.

## Risks
Most destroy functions ignore firmware command errors, which is common for cleanup but can hide leaks. Hairpin rollback must exactly mirror the create/pair order; a missed reset can leave queues ready against stale peers. Dead-peer handling must avoid sending destroy commands to a gone peer while still cleaning function-side resources later.

## Test Signals
Tests should cover command wrapper success/failure, SQ state query allocation failure, hairpin create failure during RQ creation, SQ creation, SQ pairing, and RQ pairing, plus dead-peer cleanup followed by normal destroy. Device integration tests should verify traffic through hairpin queues.
