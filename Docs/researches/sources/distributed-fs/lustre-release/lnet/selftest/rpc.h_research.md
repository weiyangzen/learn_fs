# sources/distributed-fs/lustre-release/lnet/selftest/rpc.h

## Purpose
Defines the packed SRPC wire protocol for LNet Selftest: service ids, message types, request/reply bodies, test request bodies, and the `srpc_msg` envelope.

## Important APIs And Types
Defines `enum srpc_service_type`, `enum srpc_msg_type`, generic request/reply headers, framework request/reply structs, test ping/BRW request/reply structs, `SRPC_MSG_MAGIC`, `SRPC_MSG_VERSION`, `struct srpc_msg`, and `srpc_unpack_msg_hdr()`.

## Control Flow
Callers map service ids to request/reply message types, fill the matching union body, and rely on the first generic fields for reply/bulk matchbits and status. Receivers unpack the envelope header first and then body-specific fields elsewhere.

## State And Persistence
No runtime state. The packed structs are the network ABI and must remain stable across nodes.

## Dependencies And Integration Points
Includes UAPI `lnetst.h` for session IDs, batch IDs, counters, features, and test parameters. Used by all selftest transport/framework/console/test files.

## Risks
Packed layout is fragile. Transport code depends on first-field invariants. Endian handling is split between this header and `framework.c` body unpackers, so new messages need both updates.

## Test Signals
`module.c` wire layout assertions, version/magic mismatch handling, endian-swapped messages, and service request/reply pair mapping.
