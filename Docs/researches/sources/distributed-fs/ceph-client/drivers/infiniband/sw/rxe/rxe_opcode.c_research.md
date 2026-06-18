# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_opcode.c

## Purpose

`rxe_opcode.c` is RXE's table-driven opcode definition file. It maps work request opcodes to supported operation masks per QP type and maps packet opcodes to header masks, lengths, offsets, and semantic categories.

## Important APIs, Types, and Functions

`rxe_wr_opcode_info[]` describes supported `IB_WR_*` behavior. `rxe_opcode[]` describes `IB_OPCODE_*` packet layouts for RC, UC, RD, and UD families. These tables drive validation, skb sizing, header access, requester construction, and responder execution.

## Control Flow

There are no functions. Runtime code indexes the tables: verbs posting validates WRs, requester code chooses packet opcodes and sizes headers, receive/responder code interprets masks for sequencing, access checks, resource handling, completions, and ACK behavior.

## State and Persistence Behavior

The state is static read-only table data for the module lifetime. It must remain consistent with `rxe_hdr.h` header byte sizes and packet accessor functions.

## Dependencies and Integration Points

It depends on RDMA opcode constants, `rxe_opcode.h`, and `rxe_hdr.h`. It is central to `rxe_verbs.c`, `rxe_req.c`, `rxe_recv.c`, `rxe_resp.c`, and completer logic.

## Risks and Edge Cases

Wrong masks or offsets can create malformed packets, parse the wrong fields, skip required checks, or advertise unsupported operations. New operations such as flush and atomic write require synchronized table and state-machine updates.

## Test Signals

Test every supported WR by QP type, unsupported-op rejection, RC/UC segmentation, read responses, atomics, atomic write, flush, send-with-imm, send-with-invalidate, UD/GSI sends, and malformed packet layout cases.
