# sources/distributed-fs/ceph-client/drivers/scsi/fnic/cq_enet_desc.h

## Purpose

`cq_enet_desc.h` defines the 16-byte Ethernet completion queue descriptor formats used by the Cisco vNIC/FNIC hardware path. It covers completions for Ethernet work queues and receive queues, including generic CQ metadata plus Ethernet, VLAN, checksum, RSS, FCoE SOF/EOF, CRC, and error indicators. The file is a firmware/hardware ABI helper rather than a policy module: callers pass a descriptor and receive decoded scalar fields.

## Important APIs, Types, and Functions

- `struct cq_enet_wq_desc`: Ethernet work-queue completion with `completed_index`, `q_number`, reserved bytes, and `type_color`.
- `cq_enet_wq_desc_dec()`: thin wrapper around `cq_desc_dec()` for type, color, queue number, and completed index.
- `struct cq_enet_rq_desc`: receive completion layout with packed flag fields, RSS hash, byte count, VLAN, checksum/FCoE, protocol flags, and `type_color`.
- `CQ_ENET_RQ_DESC_*` macros: masks and flag bits for SOP/EOP, ingress port, FCoE, RSS type, checksum availability, truncation, VLAN stripping, FCoE SOF/EOF, TCP/UDP/IP checksum status, protocol type, and FCS status.
- `cq_enet_rq_desc_dec()`: decodes all receive-completion fields, performs little-endian conversion for multi-byte descriptor fields, and switches `checksum_fcoe` interpretation based on the decoded FCoE bit.

## Control Flow

The decode flow starts by converting the packed `completed_index_flags`, `q_number_rss_type_flags`, and `bytes_written_flags` fields from little-endian to CPU order. It then delegates generic CQ metadata extraction to `cq_desc_dec()`. The rest of the function masks and shifts individual bitfields into one-byte booleans or scalar outputs. For non-FCoE frames, `checksum_fcoe` is returned as the network checksum. For FCoE frames, the same storage is split into SOF/EOF metadata, FC CRC status, and encapsulation error status, and the checksum output is forced to zero.

## State and Persistence Behavior

This header has no persistent state, allocation, locking, or side effects. Its only state interaction is through caller-owned descriptor memory and caller-provided output pointers. Correctness depends on callers reading a descriptor only after CQ color ownership indicates that hardware has completed writing it.

## Dependencies and Integration Points

The file depends on `cq_desc.h` for generic CQ decoding and queue-number bit constants, plus Linux byte-order helpers such as `le16_to_cpu()` and `le32_to_cpu()`. It integrates with FNIC/vNIC receive completion processing: receive CQ handlers decode these descriptors before recycling RQ buffers and dispatching Ethernet/FIP/FCoE frames into the FNIC frame handling paths.

## Risks and Edge Cases

- The descriptor layout is a hardware ABI. Field reordering, size changes, or incorrect masks will corrupt completion interpretation.
- The FCoE and non-FCoE meanings of `checksum_fcoe` overlap, so callers must trust the decoded `fcoe` flag before using checksum or SOF/EOF data.
- `desc->checksum_fcoe` is shifted directly in the FCoE EOF path rather than shifting the already converted temporary, so the code assumes the expression behaves correctly for the underlying little-endian type.
- The function writes many output pointers without null checks; it is only safe for internal callers that pass a complete output set.
- Packet truncation is reported as `packet_error`, so downstream paths must not confuse it with FC CRC or encapsulation errors.

## Test Signals

Useful signals include receive-path tests for plain Ethernet and FCoE frames, VLAN-stripped and non-stripped packets, truncated frames, RSS hash/type reporting, checksum-not-calculated cases, IPv4/IPv6/TCP/UDP flag combinations, FC CRC failures, FCoE encapsulation errors, and CQ color wrap behavior under load.
