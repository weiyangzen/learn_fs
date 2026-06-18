<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_lan.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_lan.h

## Purpose

`mpi_lan.h` defines the MPI LAN-over-Fusion message ABI: LAN send, receive-buffer posting, reset, reply context bitfields, LAN device state, and loopback mode constants. It is used by adapters exposing LAN protocol support through MPI, especially the historical LAN-over-FC path noted in `mptbase.h`.

## Important APIs, Types, and Definitions

- `MSG_LAN_SEND_REQUEST` posts a transmit packet through an SGL array and identifies the target port through `PortNumber`.
- `MSG_LAN_SEND_REPLY` returns IOC status/log info and a `BufferContext` used to correlate completion with the host buffer.
- `MSG_LAN_RECEIVE_POST_REQUEST` posts receive buckets using `BucketCount` plus a variable SGL tail.
- `MSG_LAN_RECEIVE_POST_REPLY` returns remaining bucket count, received packet offset and length, and one or more `BucketContext` values.
- `MSG_LAN_RESET_REQUEST` and `MSG_LAN_RESET_REPLY` reset a LAN port context.
- Context macros pack and unpack `LAN_REPLY_PACKET_LENGTH`, `LAN_REPLY_BUCKET_CONTEXT`, `LAN_REPLY_BUFFER_CONTEXT`, and `LAN_REPLY_FORM`. Form values distinguish receive single, receive multiple, send single, and message context replies.
- Device and loopback constants include `MPI_LAN_DEVICE_STATE_RESET`, `MPI_LAN_DEVICE_STATE_OPERATIONAL`, and `MPI_LAN_TX_MODES_ENABLE_LOOPBACK_SUPPRESSION`.

## Control Flow

The host posts receive buffers first with `MSG_LAN_RECEIVE_POST_REQUEST`, supplying one or more DMA SGEs. Firmware later completes receive work with packet offset/length and bucket context in either a normal reply or a compact context reply word. Sends use `MSG_LAN_SEND_REQUEST` with an SGL describing the packet payload, then complete with `MSG_LAN_SEND_REPLY` and a buffer context. Reset is a short request/reply flow that targets a `PortNumber` and returns IOC status/log info.

## State and Persistence Behavior

The header does not define persistent kernel state. Runtime state lives in firmware receive buckets, posted transmit buffers, per-port LAN state, and context words that the driver must preserve until completion. Device state constants are current operational state indicators; persistent LAN configuration is represented in LAN config pages from `mpi_cnfg.h`, not in this header.

## Dependencies and Integration Points

The header depends on MPI base types and `SGE_MPI_UNION`. It is included from `mptbase.h`, making the LAN ABI visible to the Fusion base and control paths. It shares status reporting through the common `IOCStatus` and `IOCLogInfo` fields, with FC LAN log-info subclass values defined in `mpi_log_fc.h`. Port capacity is advertised through `MSG_PORT_FACTS_REPLY.MaxLanBuckets` in `mpi_ioc.h`.

## Risks and Edge Cases

The SGL tails are declared as one-element arrays, so callers must allocate message frames large enough for the requested SGE count. Context macros mutate their first argument and assume callers mask and shift already-sized values; oversized packet lengths or contexts are silently truncated by masks. `MSG_LAN_RESET_REQUEST` comments show `PortNumber` at offset `05h` even though the field follows a two-byte reserved area at byte `06h`, so layout should be verified by structure offsets rather than comments. Receive replies can describe packet data beginning at a nonzero bucket offset, which consumers must honor.

## Test Signals

Useful tests include posting receive buckets, receiving single and multiple packet forms, verifying packet offset/length extraction, sending packets with expected buffer-context completion, exercising reset while buckets are posted, and checking IOC log info for LAN SGL/context errors. Build tests should cover all Fusion code including `mptbase.h` with LAN definitions enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_lan.h -->
