# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_pes.c

Purpose: packetizes one encoder access unit into a PES packet split across MPEG-TS packets, including optional PTS/DTS fields, adaptation-field stuffing, optional PCR, and payload copying.

Important APIs/types/functions: public entry point is `vidtv_pes_write_into()`. Internal helpers compute optional/header lengths, write PES header stuffing, encode PTS/DTS (`vidtv_pes_write_pts_dts()`), write PES headers (`vidtv_pes_write_h()`), write PCR bits, write TS adaptation stuffing, and write TS headers. Constants define private stream ID for S302M, PES header stuffing limit, and TS stuffing limit.

Control flow: `vidtv_pes_write_into()` aligns the starting offset if needed, then loops while access-unit bytes remain. The first TS packet reserves space for the PES header and optional PES stuffing; the first packet also reserves PCR adaptation bytes. For the final packet it computes stuffing to maintain 188-byte TS alignment and caps stuffing to the allowed maximum by reducing payload if necessary. Each iteration writes a TS header/adaptation field, writes the PES header once, copies payload, advances source pointer, and decreases remaining bytes.

State and persistence: no persistent state except the caller-owned continuity counter updated through `vidtv_ts_inc_cc()`. `last_pcr` is local and currently only updated when PCR is written.

Dependencies and integration points: uses vidtv common bounded memory helpers, TS header definitions/helpers, encoder IDs, and kernel endian/math helpers. Called by `vidtv_mux_packetize_access_units()` for each access unit.

Risks: pointer arithmetic on `void *` is a GNU C extension accepted in kernel builds. If bounded writes return 0, the loop may still continue based on logical payload sizes, so output can be shorter than expected without hard failure. PES length is always set to optional length plus AU length and does not use the PES_MAX_LEN zero-length convention mentioned in the header. PCR is written only on the first TS packet for an AU. The alignment recovery path pads with fill bytes outside a normal TS packet header, so it is a last-resort warning path.

Test signals: TS packet analyzer checks for 188-byte alignment, payload-unit-start indicator on the first packet, continuity increments, valid PTS fields, S302M private stream ID, last-packet stuffing behavior, large AU spanning many TS packets, and small-buffer overflow tests.
