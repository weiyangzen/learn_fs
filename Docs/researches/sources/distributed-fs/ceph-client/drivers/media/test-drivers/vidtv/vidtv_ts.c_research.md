# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_ts.c

## Purpose
`vidtv_ts.c` provides low-level MPEG transport-stream packet helpers for vidtv. It increments 4-bit continuity counters, emits null packets for padding, and emits PCR-only packets with an adaptation field.

## Important APIs, Types, and Functions
Public functions are `vidtv_ts_inc_cc()`, `vidtv_ts_null_write_into()`, and `vidtv_ts_pcr_write_into()`. Internal `vidtv_ts_write_pcr_bits()` converts a 27 MHz PCR counter into the 6-byte PCR base/extension encoding copied from ffmpeg-style logic. The functions use `struct vidtv_mpeg_ts`, `struct vidtv_mpeg_ts_adaption`, `struct null_packet_write_args`, and `struct pcr_write_args` declared in `vidtv_ts.h`.

## Control Flow
Null packet writing builds a TS header with PID `0x1fff`, payload-only mode, and the caller's continuity counter, copies it into the destination, increments the counter, then fills the remainder of the 188-byte packet with `0xff`. PCR writing builds a TS header for the caller's PID with adaptation-field-only mode, writes an adaptation field length of 183 with PCR flag set, writes the six PCR bytes, and pads the rest of the packet. PCR packets intentionally do not increment the continuity counter, following the cited MPEG rule for adaptation-only packets.

## State and Persistence
No module-level state is stored. The only mutable state is the caller-owned continuity-counter byte. Destination data is written into caller-owned buffers via vidtv safe copy/fill helpers.

## Dependencies and Integration Points
The file depends on `linux/math64.h`, printk ratelimiting, `vidtv_common.h`, and `vidtv_ts.h`. PSI serialization and the transport muxer use these routines to pad streams and insert timing references.

## Risks and Edge Cases
All writers assume the caller supplied a valid buffer, offset, size, and continuity pointer. Short buffers rely on `vidtv_memcpy()`/`vidtv_memset()` behavior to avoid overflow, but the functions still return the number of bytes attempted or copied by helpers and only warn if the final packet size is not exactly 188 bytes. PCR encoding uses integer division by 300 and expects a PCR value in 27 MHz ticks.

## Test Signals
Tests should assert null packets are exactly 188 bytes, have sync byte `0x47`, PID `0x1fff`, valid stuffing, and continuity wrap from 15 to 0. PCR tests should decode the written adaptation field and compare PCR base/extension against known input counter values.
