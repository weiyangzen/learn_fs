# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_ts.h

## Purpose
`vidtv_ts.h` defines vidtv's MPEG-TS packet constants, packed header structures, write-argument types, and prototypes for null packet and PCR packet helpers.

## Important APIs, Types, and Functions
Constants include `TS_SYNC_BYTE`, `TS_PACKET_LEN`, `TS_PAYLOAD_LEN`, `TS_NULL_PACKET_PID`, `TS_CC_MAX_VAL`, `TS_LAST_VALID_PID`, and `TS_FILL_BYTE`. `struct vidtv_mpeg_ts` models the 4-byte TS header with sync byte, PID bitfield, scrambling/adaptation/payload flags, and continuity counter. `struct vidtv_mpeg_ts_adaption` models the adaptation-field prefix. Public APIs are `vidtv_ts_inc_cc()`, `vidtv_ts_null_write_into()`, and `vidtv_ts_pcr_write_into()`.

## Control Flow
Callers construct `null_packet_write_args` or `pcr_write_args` with destination buffer metadata and a continuity-counter pointer, then call the corresponding writer. The functions serialize one full TS packet at the supplied offset.

## State and Persistence
The header defines no storage. Continuity state is external and passed by pointer. The packed structures are transient serialization helpers.

## Dependencies and Integration Points
It includes `linux/types.h` and is consumed by PSI, muxing, and other vidtv TS-generation code. `TS_LAST_VALID_PID` is also used by PSI logic to return an invalid sentinel when a PMT PID is not found.

## Risks and Edge Cases
The C bitfield layout in the packed TS header is implementation-sensitive; the code compensates for PID endianness with explicit big-endian fields but still relies on local bitfield packing for flags. Callers must keep offsets TS-packet aligned when required by higher-level packetizers.

## Test Signals
Compile-time structure-size checks and runtime packet decoding should verify header layout, continuity counter wrap, null PID, adaptation-field flags, and payload-length assumptions.
