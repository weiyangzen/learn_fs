# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_protocol.h

## Purpose

`drbd_protocol.h` defines the DRBD on-wire protocol command numbers, feature flags, packet headers, and packed payload structures used by the replication data and metadata sockets. It is a compatibility-critical contract between DRBD peers and between protocol-version-specific send/receive code paths.

## Important APIs, Types, And Functions

- `enum drbd_packet` assigns stable command IDs for data packets, resync packets, barriers, bitmaps, authentication, state changes, pings/acks, online verify, checksum resync, compressed bitmap transfer, disconnect/state requests, trim/write-same/zeroes, handshake packets, and feature negotiation.
- Header structures `p_header80`, `p_header95`, and `p_header100` describe protocol-era packet headers. They differ in length width, volume field support, and padding/alignment.
- Data path payloads include `p_data`, `p_trim`, `p_wsame`, `p_block_ack`, `p_block_req`, and `p_block_desc`.
- Negotiation and control payloads include `p_connection_features`, `p_protocol`, `p_uuids`, `p_rs_uuid`, `p_sizes`, `p_state`, `p_req_state`, `p_req_state_reply`, and older `p_drbd06_param`.
- Resync parameter layouts include `p_rs_param`, `p_rs_param_89`, and `p_rs_param_95`, reflecting protocol-version evolution.
- Feature flags `DRBD_FF_TRIM`, `DRBD_FF_THIN_RESYNC`, `DRBD_FF_WSAME`, and `DRBD_FF_WZEROES` advertise optional wire capabilities.
- Data packet flags `DP_RW_SYNC`, `DP_MAY_SET_IN_SYNC`, `DP_FUA`, `DP_FLUSH`, `DP_DISCARD`, `DP_SEND_RECEIVE_ACK`, `DP_SEND_WRITE_ACK`, `DP_WSAME`, and `DP_ZEROES` encode block-layer semantics and protocol acknowledgement expectations.
- `enum drbd_conn_flags` defines connection flags sent in `p_protocol`, including discard-my-data and dry-run.
- `enum drbd_bitmap_code` defines compressed bitmap encoding values.
- `DRBD_SOCKET_BUFFER_SIZE` fixes bitmap packet sizing to 4096 bytes.

## Control Flow

This header has no executable control flow, but it controls runtime dispatch in receiver and sender code. Incoming packet command IDs select decode handlers, and negotiated protocol version/features determine which header and payload layout is valid. For example, older protocol 80 headers can only represent smaller payload lengths, protocol 95 supports larger packets, and protocol 100 includes a volume number. Optional queue limits in `p_sizes` are present only when the negotiated feature set includes `DRBD_FF_WSAME`.

Feature flags gate higher-level behavior in files such as `drbd_nl.c`: TRIM/discard support depends on `DRBD_FF_TRIM`, maximum discard sizing changes with `DRBD_FF_WSAME`, thin resync can use `P_RS_THIN_REQ`/`P_RS_DEALLOCATED`, and write-zeroes support depends on `DRBD_FF_WZEROES`. Resync parameter structures evolve by protocol version to add checksum algorithms and controller settings while preserving older layouts.

## State And Persistence Behavior

The structures represent transient wire state rather than local persistent metadata. However, many fields carry persistent or state-machine-significant values: UUID arrays, current/bitmap sync UUIDs, disk sizes, requested user size, current exported size, queue limits, role/disk/connection state, resync rates, protocol mode, after-split-brain policies, and authentication/integrity algorithm names. Mis-encoding these fields can cause persistent metadata divergence, incorrect resync decisions, or incompatible peer negotiation.

All packet structures are packed and use network byte order except documented local echo handles such as `block_id` and barrier fields. Alignment notes are explicit because payload offsets must stay long-aligned across 32-bit and 64-bit systems.

## Dependencies And Integration Points

The header depends on Linux fixed-width integer types, `SHARED_SECRET_MAX`, and DRBD constants from surrounding headers. It is consumed by DRBD sender, receiver, handshake, bitmap, resync, online-verify, request, and configuration code. It also informs queue-limit negotiation and discard/write-same/write-zeroes behavior in administrative code.

## Risks

- Command IDs, flags, structure layout, and field meanings are wire ABI. Changing them without a protocol version bump or feature flag would break interoperability.
- Packed structures and flexible arrays require careful size checks in send/receive code to avoid overreads, truncation, or alignment bugs.
- Some comments document overloaded feature semantics, especially `DRBD_FF_WSAME`; tests and code must treat those historical meanings consistently.
- The distinction between discard and write-zeroes is data-integrity sensitive on thin-provisioned storage. Incorrect `DP_DISCARD`/`DP_ZEROES` or feature negotiation can expose stale backend data or force unwanted allocation.
- Header choice by protocol version affects maximum packet sizes. Mismatches can corrupt stream parsing.

## Test Signals

Compatibility tests should connect peers across supported protocol versions and verify header selection, feature negotiation, max bio/discard/write-zeroes behavior, resync parameter exchange, UUID exchange, state-change requests/replies, authentication, compressed bitmap transfer, and online verify packets. Static/build tests should assert packed sizes and offsets for wire structs. Fuzz or negative tests should reject invalid lengths, unsupported optional commands, unknown bitmap encodings, and inconsistent feature/command combinations.
