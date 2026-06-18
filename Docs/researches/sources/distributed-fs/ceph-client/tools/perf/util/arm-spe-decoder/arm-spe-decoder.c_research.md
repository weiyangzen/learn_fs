# sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-decoder.c

## Purpose
Implements the high-level Arm SPE decoder. It pulls raw trace buffers through a callback, decodes packets with the packet decoder, normalizes address payloads, and accumulates packets into one `arm_spe_record` per SPE sample record.

## Important APIs, Types, and Functions
`arm_spe_decoder_new()` validates `get_trace`, allocates `struct arm_spe_decoder`, and stores callback state.
`arm_spe_decoder_free()` releases the decoder.
`arm_spe_decode()` calls `arm_spe_read_record()`.
`arm_spe_get_data()` refills the current trace buffer from the callback.
`arm_spe_get_next_packet()` skips PAD packets and advances buffer pointers, returning `-EBADMSG` after bad packet decode.
`arm_spe_calc_ip()` strips/repairs address metadata for instruction, branch, data virtual, data physical, and previous-branch address packets.
`arm_spe_read_record()` loops over packets until timestamp, end, input exhaustion, or error and fills `arm_spe_record` fields.

## Control Flow
The decoder refills when its current buffer is empty, decodes one packet at a time, skips padding, and updates record fields based on packet type. Timestamp and end packets terminate the current record. Address packets populate from/to/data/previous-branch addresses. Counter packets currently use total latency. Context, operation type, event, and data-source packets update corresponding record fields.

## State and Persistence
`struct arm_spe_decoder` stores callback pointers, current buffer pointer/length, the last packet, and the current output record. Each record is zeroed before reading and `context_id` defaults to all-ones. No persistent storage is used.

## Dependencies and Integration Points
Depends on `arm-spe-pkt-decoder.h` for packet parsing and encoding macros, `auxtrace`-style buffer callbacks for trace input, and perf debug helpers. Downstream Arm SPE perf code consumes `arm_spe_record` to synthesize samples/events.

## Risks
Bad packets advance only one byte before returning an error, so callers must decide whether to retry/resynchronize. Unsupported address indices warn once per index and otherwise return raw payload. Operation decoding must track Arm SPE architectural extensions; missing subclass bits produce incomplete `record.op`.

## Test Signals
Feed synthetic SPE traces containing padding, timestamp-terminated records, end-terminated records, all address indices, total latency counters, context packets, load/store subclasses, SVE/SME/GCS branches, malformed packets, and buffer-boundary splits.
