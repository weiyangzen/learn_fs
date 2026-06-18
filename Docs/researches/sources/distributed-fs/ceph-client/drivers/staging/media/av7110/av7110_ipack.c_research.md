# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ipack.c

## Purpose
This file implements the AV7110 PES instant repacker. It consumes arbitrary byte chunks, recognizes MPEG PES start codes and headers, accumulates a complete or bounded packet in an `ipack`, optionally repairs AC3 private-stream substream metadata, and emits repacked PES buffers through a caller-supplied callback.

## Important APIs and Functions
`av7110_ipack_init()` allocates the packet buffer with `vmalloc()`, records the callback, clears repack flags, and calls `av7110_ipack_reset()`. `av7110_ipack_reset()` clears parser state fields such as `found`, `cid`, `plength`, flags, PTS bookkeeping, and byte counts. `av7110_ipack_free()` releases the `vmalloc()` buffer. `av7110_ipack_flush()` forces emission for packets with indefinite maximum length when enough bytes have been found.

`av7110_ipack_instant_repack()` is the core streaming parser. It searches for `00 00 01`, validates the stream ID against MPEG program/private/audio/video ranges, reads PES length and MPEG1/MPEG2 header fields, copies header/payload bytes into the packet buffer through `write_ipack()`, emits complete packets, resets state, and recursively processes trailing bytes in the same input chunk. `send_ipack()` finalizes length bytes and invokes `p->func()`. In MPEG2 private stream 1 with `p->repack_subids`, it uses `dvb_filter_get_ac3info()` to recompute AC3 frame counts and offsets.

## Control Flow and State
The parser is incremental. `p->found` is a byte-position state variable through start code, stream ID, PES length, and optional header. `p->mpeg` selects MPEG1 versus MPEG2 header rules. `p->done` marks stream IDs that should be skipped rather than emitted. `p->plength` defaults to `MMAX_PLENGTH - 6` for unspecified PES length, causing flush behavior to be caller-driven. `write_ipack()` handles output buffer overflow by filling the remaining space, sending a partial packet, and recursively writing the rest into a fresh packet with a preserved PES header.

The only persistence is the in-memory `struct ipack` and its allocated buffer. There is no locking in this file; callers must serialize access to an `ipack`.

## Dependencies and Integration Points
It depends on `dvb_filter.h` for stream IDs, flags, `struct ipack`, `MMAX_PLENGTH`, and AC3 parsing declarations, and on `av7110_ipack.h` for public prototypes. It uses `vmalloc()` because packet buffers can be larger than small stack or slab-friendly allocations. The callback integrates with AV7110 MPEG/audio/video paths that need repacked PES output.

## Risks and Test Signals
Risks include malformed PES causing parser desynchronization, AC3 metadata adjustment using insufficient bytes, recursion depth on pathological oversized input, caller-provided buffer sizes too small for expected repack output, and lack of internal locking. Test signals include feeding split start codes across calls, MPEG1 and MPEG2 PES with PTS/DTS, private stream AC3 packets, unspecified-length PES with flush, small output buffer boundaries, malformed stream IDs, and callback byte lengths matching PES length fields.
