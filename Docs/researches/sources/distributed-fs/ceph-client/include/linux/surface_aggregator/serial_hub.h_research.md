<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_aggregator/serial_hub.h -->
# sources/distributed-fs/ceph-client/include/linux/surface_aggregator/serial_hub.h

## Purpose

`serial_hub.h` defines the low-level Surface Serial Hub protocol used below SSAM controller requests. It describes SSH frame and command wire formats, payload sizing and offsets, CRC calculation, request/event ID encoding, known target IDs/categories, packet transport state, and request transport state.

## Important APIs, types, and functions

Important wire types are `struct ssh_frame` and `struct ssh_command`, both packed and size-asserted. Sizing macros include `SSH_FRAME_MAX_PAYLOAD_SIZE`, `SSH_COMMAND_MAX_PAYLOAD_SIZE`, `SSH_MSG_LEN_BASE`, `SSH_MESSAGE_LENGTH()`, and `SSH_COMMAND_MESSAGE_LENGTH()`. Offset helpers locate fields in raw messages. `ssh_crc()` wraps `crc_itu_t()`. Request ID helpers classify event IDs and skip reserved event IDs. Transport state is represented by `struct ssam_span`, `struct ssh_packet`, `struct ssh_packet_ops`, `struct ssh_request`, and `struct ssh_request_ops`; helpers manage references and attach caller-owned buffers.

## Control flow

Outbound control starts with a raw message buffer containing SYN, frame, frame CRC, optional command payload, and payload CRC. A packet is queued with priority derived from base class and retry count. Sequenced data packets require ACK tracking; request transport wraps packets and waits for matching command responses by request ID. Inbound command frames can be classified as responses or EC events via reserved request IDs, then delivered to request completion or notifier logic above.

## State and persistence behavior

The header defines volatile transport state rather than persistent storage. `ssh_packet.state` and `ssh_request.state` track locked, queued, pending, transmitting, transmitted, acknowledged/response-received, canceled, and completed phases. Timestamps support timeout handling. Buffers are non-owned spans; callers must preserve raw data until release callbacks fire. References are managed by `kref` through packet/request get/put helpers.

## Dependencies and integration points

It depends on CRC-ITU-T, krefs, ktime, lists, and core integer types. It feeds `controller.h` request construction, the SSAM serial transport driver, Surface EC event dispatch, and target/category constants used by Surface client drivers.

## Risks and test signals

Protocol layout mistakes are high impact because structures are packed hardware/firmware ABI. Risks include stale caller-owned buffers, incorrect CRC coverage, event/request ID overlap, invalid target IDs, retry priority overflow beyond four low bits, and missing barriers around transport state. Tests should validate exact wire sizes/offsets, CRC generation, request ID rollover around reserved event IDs, target ID validity, packet reference release ordering, ACK/NAK handling, timeout paths, and event versus response dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/surface_aggregator/serial_hub.h -->
