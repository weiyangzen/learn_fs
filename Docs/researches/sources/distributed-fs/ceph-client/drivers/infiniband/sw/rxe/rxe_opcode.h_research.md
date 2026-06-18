# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_opcode.h

## Purpose

`rxe_opcode.h` defines the mask vocabulary and table structures used to classify RXE work requests and packet opcodes.

## Important APIs, Types, and Functions

It defines `enum rxe_wr_mask`, `struct rxe_wr_opcode_info`, `enum rxe_hdr_type`, `enum rxe_hdr_mask`, `struct rxe_opcode_info`, `OPCODE_NONE`, `RXE_NUM_OPCODE`, and the external `rxe_wr_opcode_info[]`/`rxe_opcode[]` tables.

## Control Flow

The header has no executable logic. Requester, responder, receive, and verbs code branch on these mask bits instead of duplicating opcode lists.

## State and Persistence Behavior

There is no mutable state. The enums and structs are persistent internal contracts for operation semantics and packet layout.

## Dependencies and Integration Points

It integrates RDMA core opcode constants with RXE header accessors, packet builders/parsers, and posting checks.

## Risks and Edge Cases

Mask bit uniqueness and composite masks are correctness-critical. Adding a header type or operation requires table, accessor, and state-machine updates.

## Test Signals

Compile all include users and run protocol tests that exercise each mask category and header accessor offset.
