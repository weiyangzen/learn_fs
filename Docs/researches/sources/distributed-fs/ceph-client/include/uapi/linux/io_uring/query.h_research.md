
# sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/query.h

## Purpose

`io_uring/query.h` defines the io_uring query-registration ABI for discovering supported opcodes, ring/setup/enter flags, zcrx capabilities, and shared SQ/CQ header sizing. The complete 72-line file was read.

## Important APIs, Types, and Functions

Structures are `io_uring_query_hdr`, `io_uring_query_opcode`, `io_uring_query_zcrx`, and `io_uring_query_scq`. Query op IDs are `IO_URING_QUERY_OPCODES`, `IO_URING_QUERY_ZCRX`, and `IO_URING_QUERY_SCQ`.

## Control Flow

User space submits `IORING_REGISTER_QUERY` requests with a query header. The kernel fills query-specific payloads and can chain entries through `next_entry`.

## State and Persistence Behavior

The header reports capability state rather than storing state. Results describe the current kernel's supported request/register/query opcodes, feature flags, setup/enter/SQE flags, zcrx properties, and SQ/CQ header layout.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with `io_uring.h`, zcrx registration, liburing capability probing, and no-ring query paths for opcode support.

## Risks and Edge Cases

Query payload sizes and chaining must be validated. User space must tolerate newer query opcodes and partial support. Capability bitmasks can exceed assumptions if code hard-codes old limits.

## Test Signals

Tests should query opcode support without a ring where allowed, query zcrx and SCQ data, validate size/result handling, chain multiple entries, and reject unknown query opcodes cleanly.
