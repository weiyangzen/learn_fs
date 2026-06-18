# sources/compression/zlib/gzread.c

## Purpose
`gzread.c` implements all read-side `gzFile` operations, including gzip auto-detection, transparent copying, decompression, buffered character operations, pushback, line reads, direct-mode reporting, and read close.

## Important APIs, Types, and Functions
Public functions are `gzread()`, `gzfread()`, `gzgetc()`, `gzgetc_()`, `gzungetc()`, `gzgets()`, `gzdirect()`, and `gzclose_r()`. Internal helpers are `gz_load()`, `gz_avail()`, `gz_look()`, `gz_decomp()`, `gz_fetch()`, `gz_skip()`, and `gz_read()`.

## Control Flow, State, and Persistence
The read path lazily allocates input/output buffers and initializes an inflate stream on first need. `gz_look()` decides whether the input is gzip or transparent data, `gz_fetch()` dispatches among header lookup, raw copy, and decompression, and `gz_read()` drains existing output before fetching or direct-filling the user buffer. State persists in `how`, `direct`, `junk`, `again`, `eof`, `past`, `skip`, `x.have`, `x.next`, and `x.pos`. `gzclose_r()` frees buffers, ends inflate, closes the descriptor, and returns deferred EOF/data status.

## Dependencies and Integration Points
It uses `gzguts.h`, `read()`, `close()`, `inflateInit2(15 + 16)`, `inflateReset()`, and `inflate()`. It cooperates with `gzlib.c` for open/reset/seek/error state and with `gzclose.c` for generic close dispatch.

## Risks and Test Signals
Risks include nonblocking `EAGAIN` handling, distinguishing trailing garbage from corrupt gzip data, multi-member gzip transitions, pushback buffer room, and deferred errors after returning already-produced bytes. Tests should cover gzip, transparent, empty, truncated, concatenated-member, pushed-back, line-read, nonblocking, and seek-skip reads.
