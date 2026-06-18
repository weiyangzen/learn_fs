# sources/distributed-fs/ceph-client/fs/jffs2/compr_rtime.c

## Purpose
`compr_rtime.c` implements JFFS2's simple rtime compressor. The algorithm records the last output/source position for each byte value and emits pairs of literal byte plus repeat length, targeting a byte-oriented, low-complexity compression format.

## Important APIs, Types, And Functions
The central callbacks are `jffs2_rtime_compress()` and `jffs2_rtime_decompress()`. The static `jffs2_rtime_comp` registers priority `JFFS2_RTIME_PRIORITY`, name `rtime`, id `JFFS2_COMPR_RTIME`, and optional disabled state under `JFFS2_RTIME_DISABLED`. `jffs2_rtime_init()` and `jffs2_rtime_exit()` register and unregister the backend.

## Control Flow
Compression initializes a 256-entry position table, then emits a literal byte followed by the number of following bytes that match the last occurrence of that literal's value, capped at 255. It stops when input is exhausted or output capacity cannot hold another pair. It fails if the encoded size is not smaller than the amount consumed. Decompression reads literal/repeat pairs, writes the literal, consults the previous position table for that value, and copies repeated bytes either byte-by-byte for overlap or with `memcpy()`.

## State And Persistence Behavior
There is no global workspace; all algorithm state is stack-local. On flash, rtime data is identified only by `JFFS2_COMPR_RTIME` in the raw inode compression field.

## Dependencies And Integration Points
The backend depends on kernel string/types headers and `compr.h`. It integrates through the global compressor list and is selected by priority, size, or explicit policy.

## Risks And Test Signals
The decompressor trusts the encoded stream enough to read pairs until `destlen` is satisfied; malformed streams need coverage for short input and overrun prevention. Compression can partially consume input, which callers must honor via updated `*sourcelen`. Tests should include repeated-byte data, random incompressible data, boundary destination sizes, overlapping repeat copies, and compatibility reads of existing rtime-compressed media.
