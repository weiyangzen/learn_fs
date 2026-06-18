# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_param.h

## Purpose

`rxe_param.h` defines RXE default device, port, resource, MTU, and protocol limits exposed through RDMA attributes and used internally for validation and scheduling.

## Important APIs, Types, and Functions

It provides `rxe_mtu_int_to_enum()`, `eth_mtu_int_to_enum()`, `enum rxe_device_param`, `enum rxe_port_param`, and `enum rxe_port_info_param`. Constants cover QP/CQ/PD/SRQ/MR/MW limits, access flags, atomics, flush, inflight skb watermarks, and workqueue iteration limits.

## Control Flow

Inline MTU helpers are used when deriving IB MTUs from Ethernet MTUs. Constants are consumed during device initialization, query verbs, QP/SRQ validation, pool setup, requester backpressure, and task execution.

## State and Persistence Behavior

No mutable state is stored. Constants become persistent `rxe_dev` and port attributes once an RXE device is initialized.

## Dependencies and Integration Points

It includes RXE UAPI definitions and integrates with verbs, QP, SRQ, pool, network MTU, and task code.

## Risks and Edge Cases

Very large defaults require allocation paths to do real memory checks. MR/MW index ranges affect rkey/lkey classification. MTU conversion depends on correct RXE max header length.

## Test Signals

Check query-device/query-port attributes, netdev MTU changes, near-limit QP/SRQ/CQ/MR/MW creation, rkey MW classification, skb backpressure, and task fairness.
