<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/tstee_private.h -->
# sources/distributed-fs/ceph-client/drivers/tee/tstee/tstee_private.h

## Purpose

`tstee_private.h` defines the Trusted Services RPC protocol constants and private driver state used by `tstee/core.c`. It encodes FF-A direct-message register positions, management/service opcodes, status bits, and per-device/per-session structures.

## Important APIs, Types, and Functions

`TS_RPC_UUID` is the protocol UUID matched on the FF-A bus. `TS_RPC_PROTOCOL_VERSION` is version 1. Control register helpers define opcode/interface masks, extractors, packer `TS_RPC_CTRL_PACK_IFACE_OPCODE()`, and SAP return/error bits. Management operations include GET_VERSION, RETRIEVE_MEM, RELINQ_MEM, and SERVICE_INFO with register indexes for handles, tags, status, and interface ID. Service-call indexes define memory handle, request length, client ID, RPC status, service status, and response length.

`struct tstee` stores the FF-A device, TEE device, and shared-memory pool. `struct ts_session` stores the Trusted Services interface ID. `struct ts_context_data` stores an xarray of sessions for each TEE context.

## Control Flow

The constants are consumed by `core.c` to format five 32-bit FF-A direct-message arguments. Management calls are sent during probe, session open, and shared-memory register/unregister. Service calls are sent during TEE invoke using the session's interface ID and the lower 16 bits of `arg->func` as opcode.

## State and Persistence Behavior

The header defines runtime-only device and context structures. Sessions persist for the lifetime of a TEE context or until explicitly closed. FF-A memory handles persist in individual `tee_shm` objects until unregistered.

## Dependencies and Integration Points

It depends on Arm FF-A types, bitops/bitfield helpers, TEE core types, UUID, xarray, and integer types. It is private to the tstee driver and tied to the Trusted Services service access protocol ABI referenced in the file comment.

## Risks and Edge Cases

Register indexes and bitfields are ABI constants; any drift from the Trusted Services specification breaks all messaging. The control register reserves SAP status bits but current core logic mostly checks per-call status registers. Interface ID is narrowed to `u8`, so service-info responses above `U8_MAX` are rejected by core. There are no compile-time assertions for the assumed five-register direct-message width.

## Test Signals

Tests should verify packed control register values, opcode/interface extraction, UUID matching, protocol version check, every management register index, interface ID boundary handling, and compatibility with Trusted Services protocol documentation for version 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/tstee_private.h -->
