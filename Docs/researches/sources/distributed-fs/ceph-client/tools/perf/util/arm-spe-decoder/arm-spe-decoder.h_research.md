# sources/distributed-fs/ceph-client/tools/perf/util/arm-spe-decoder/arm-spe-decoder.h

## Purpose
Defines the public Arm SPE decoded-record API, operation/event bit flags, vendor data-source enums, buffer callback contract, and decoder object layout.

## Important APIs, Types, and Functions
`struct arm_spe_record` is the decoded sample record containing event type bits, error, operation flags, latency, instruction/target/previous branch IPs, timestamp, virtual/physical data addresses, context id, and data source.
`struct arm_spe_buffer` carries raw trace buffer pointer, length, offset, and trace number.
`struct arm_spe_params` provides the `get_trace` callback and opaque data.
`struct arm_spe_decoder` stores callback state, current record, current buffer, and last packet.
`arm_spe_decoder_new()`, `arm_spe_decoder_free()`, and `arm_spe_decode()` are the public lifecycle/decode API.
Enums define first-level operation classes, second-level load/store and branch flags, common data-source values, and vendor-specific AmpereOne/Hisi HIP source encodings.

## Control Flow
Clients initialize `arm_spe_params`, allocate a decoder, repeatedly call `arm_spe_decode()`, and read `decoder->record` after successful decode. Event macros map packet event bits into named record flags.

## State and Persistence
The decoder is stateful across calls through current buffer pointer/length and callback data. Records are overwritten on each decode. No ownership of trace buffers is implied by the header; the provider controls buffer lifetime.

## Dependencies and Integration Points
Includes `arm-spe-pkt-decoder.h` for packet definitions and event bit positions. Used by Arm SPE auxtrace processing to turn byte streams into perf records.

## Risks
Operation flags share a 32-bit field with high bits up to bit 30; additions must avoid overflow and collisions. Callback buffer lifetime must outlive decode consumption. Vendor data-source enums require downstream interpretation to avoid mixing encodings.

## Test Signals
Compile API users against the header, verify bit masks match packet decoder event enum positions, and test callback-driven decode with multiple buffers and zero-length end-of-stream.
