# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_msgb.h

## Purpose

This header provides small inline builders for Surface Serial Hub protocol messages. It writes SYN markers, frame headers, ACK/NAK packets, command payloads, and CRCs into caller-supplied buffers for the Surface Aggregator request path.

## Important APIs, Types, And Functions

`struct msgbuf` tracks begin/end/current pointers. Helpers are `msgb_init()`, `msgb_bytes_used()`, `msgb_push_u16()`, `msgb_push_syn()`, `msgb_push_buf()`, `msgb_push_crc()`, `msgb_push_frame()`, `msgb_push_ack()`, `msgb_push_nak()`, and `msgb_push_cmd()`. Internal push helpers write raw `u8` and little-endian `u16` values. `msgb_push_cmd()` builds a DATA_SEQ frame containing `struct ssh_command`, request IDs, target/category/source/instance/command fields, payload, and CRC.

## Control Flow

Callers initialize `msgbuf` with a pre-sized span, push a SYN marker, push a frame header and frame CRC, write optional command payload, then append payload CRC. `ssam_request_write_data()` in `controller.c` is the primary command-message caller and checks payload and total message size before using these helpers.

## State And Persistence

The only state is the transient buffer cursor. The header owns no persistent state and performs no allocation. Resulting bytes are queued into the SSH packet/request transport.

## Dependencies And Integration Points

It depends on unaligned little-endian helpers, Surface Aggregator controller and serial-hub public headers, `ssh_crc()`, SSH frame constants, `struct ssh_frame`, `struct ssh_command`, and `struct ssam_request`. It is tightly coupled to `controller.c` request serialization.

## Risks

Some helpers check capacity (`msgb_push_u16()`, `msgb_push_frame()`, command header check), but `msgb_push_buf()` does not check bounds itself and depends on caller prevalidation. If a warning path returns early, later pushes may still execute in some callers, so total size checks before construction are essential. CRC coverage must match the EC protocol exactly: frame CRC covers the frame header, and command CRC covers command struct plus payload.

## Test Signals

Useful tests are byte-for-byte command frame fixtures, ACK/NAK fixture tests, CRC validation, boundary payload sizes at `SSH_COMMAND_MAX_PAYLOAD_SIZE`, undersized-buffer warning tests, and integration tests where EC accepts requests serialized by `ssam_request_write_data()`.
