# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_parser.c

## Purpose
Provides zero-copy parsing and validation helpers for SSH messages used by the Surface Aggregator serial hub. It validates SYN alignment, frame and payload CRCs, maximum message length, and command payload shape.

## Important APIs, Types, And Functions
`sshp_find_syn()` searches a span for complete or partial SSH SYN bytes and returns the remaining aligned span. `sshp_parse_frame()` validates a complete SSH frame and returns a `struct ssh_frame *` plus payload span. `sshp_parse_command()` validates command payload length and returns a `struct ssh_command *` plus command-data span. Internal helpers `sshp_validate_crc()` and `sshp_starts_with_syn()` implement CRC comparison and SYN prefix detection.

## Control Flow
RX code first calls `sshp_find_syn()` to align to the next possible message. `sshp_parse_frame()` then confirms the span starts with SYN, has enough bytes for a minimal message, validates the frame CRC over `struct ssh_frame`, checks payload length against caller-provided `maxlen`, waits for a complete payload if needed, validates payload CRC, and finally returns pointers into the source buffer. Request-layer code later calls `sshp_parse_command()` on data-frame payloads to interpret command headers and payload bytes.

## State And Persistence Behavior
The parser is stateless. It mutates only output pointers and lengths. It does not allocate memory, retain references, or copy message payloads. Returned frame and command pointers alias the caller's RX buffer and are valid only while that buffer remains stable.

## Dependencies And Integration Points
Uses `linux/unaligned.h`, device logging, and SSH protocol macros/types from `linux/surface_aggregator/serial_hub.h`. Integrated directly by `ssh_packet_layer.c` for frame parsing and by `ssh_request_layer.c` for command parsing.

## Risks
`sshp_find_syn()` indexes `src->ptr[src->len - 1]`; callers must not pass zero-length spans. `sshp_parse_frame()` treats incomplete frames as success with `*frame == NULL`, so callers must distinguish incomplete data from valid complete frames. Length and CRC validation are robust, but any future protocol extension must keep `maxlen` consistent with the RX buffer capacity.

## Test Signals
Parser tests should cover valid ACK/NAK/data frames, bad SYN, partial SYN at buffer end, incomplete minimal frame, invalid frame CRC, oversized payload length, incomplete payload, invalid payload CRC, command payload too short, zero-length command data, and aliasing behavior where returned spans point inside the original buffer.
