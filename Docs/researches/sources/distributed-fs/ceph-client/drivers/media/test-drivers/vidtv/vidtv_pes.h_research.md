# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_pes.h

Purpose: PES packetization structure definitions and API for vidtv.

Important APIs/types/functions: defines PES constants, packed structs for optional PTS and PTS/DTS fields, optional PES header flags, PES base header, `struct pes_header_write_args`, `struct pes_ts_header_write_args`, `struct pes_write_args`, and prototype `vidtv_pes_write_into()`.

Control flow: header only; it describes the inputs used by `vidtv_pes.c` to write PES headers and split payload into TS packets.

State and persistence: packetization state is caller supplied. The continuity counter pointer lets the writer persist TS continuity across calls for a PID.

Dependencies and integration points: includes Linux types and `vidtv_common.h`; used by mux and PES implementation.

Risks: callers must provide valid buffer size/offset, access-unit length, stream ID/PID, continuity counter, and timestamp flags. Incorrect values can produce syntactically invalid TS even if memory writes remain bounded.

Test signals: compile coverage, PES/TS conformance checks for generated headers, and mux-level service playback/scan tests.
