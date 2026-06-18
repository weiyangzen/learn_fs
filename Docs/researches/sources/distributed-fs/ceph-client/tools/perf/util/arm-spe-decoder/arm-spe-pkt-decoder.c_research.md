# sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-pkt-decoder.c

## Purpose
Implements low-level Arm SPE packet decoding and human-readable packet descriptions. It recognizes SPE header encodings, extracts little-endian payloads, handles padding/alignment/end packets, and formats events, operation types, addresses, context, counters, timestamps, and data-source packets.

## Important APIs, Types, and Functions
`arm_spe_get_packet()` is the public parser. It calls `arm_spe_do_get_packet()` and coalesces consecutive zero PAD bytes up to 16 bytes.
`arm_spe_pkt_name()` returns a short packet type name.
`arm_spe_pkt_desc()` formats a packet into a caller-provided buffer.
`arm_spe_payload_len()` decodes the payload size from header bits.
`arm_spe_get_payload()` validates length and reads 1/2/4/8-byte little-endian payloads.
Specific packet helpers set type/index and consume payloads for timestamp, events, data source, context, op type, counter, address, alignment, pad, and end.
Formatting helpers include `arm_spe_pkt_desc_event()`, `arm_spe_pkt_desc_op_type()`, `arm_spe_pkt_desc_addr()`, and `arm_spe_pkt_desc_counter()`.

## Control Flow
Packet decode starts with byte 0. Special headers handle PAD, END, TIMESTAMP, events, source, context, and op type. Extended headers are detected through `SPE_HEADER0_EXTENDED`; alignment is a special extended header, otherwise byte 1 is reused for address/counter classification. Address and counter packets derive their index from short or extended header bits. Description formatting switches by packet type and falls back to raw `name payload (index)` formatting on unknown subtype errors.

## State and Persistence
Parser functions are stateless aside from static packet-name tables. Description output mutates only caller-provided buffers. No heap allocation or persistent state is used.

## Dependencies and Integration Points
Depends on Linux bit macros, unaligned little-endian reads, and packet constants from `arm-spe-pkt-decoder.h`. Integrated by `arm-spe-decoder.c` for record construction and by diagnostic tooling for packet dumps.

## Risks
`arm_spe_pkt_name()` indexes the name array directly and assumes a valid enum. Extended-header handling returns `ARM_SPE_BAD_PACKET` for a single byte extended header rather than `NEED_MORE_BYTES`, which affects callers at buffer boundaries. Formatting truncation is detected but represented as an internal error then falls back for packet subtype errors only.

## Test Signals
Use byte-level fixtures for every packet class, payload size, short and extended address/counter indices, alignment padding, consecutive PAD coalescing, malformed headers, truncated payloads, and descriptions for all event/op/address/counter variants.
