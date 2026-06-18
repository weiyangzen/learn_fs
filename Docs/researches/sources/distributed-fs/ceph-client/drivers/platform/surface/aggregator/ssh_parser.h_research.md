# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_parser.h

## Purpose
Declares the SSH parser API and provides small inline buffer helpers used by the packet RX thread to accumulate bytes and expose parseable spans.

## Important APIs, Types, And Functions
`struct sshp_buf` tracks a byte pointer, used length, and capacity. Inline helpers initialize, allocate, free, drop consumed bytes with `memmove()`, drain bytes from a `kfifo`, and create an `ssam_span` at a buffer offset. The declared parser functions are `sshp_find_syn()`, `sshp_parse_frame()`, and `sshp_parse_command()`.

## Control Flow
The packet RX thread allocates one `sshp_buf`, repeatedly reads from its kfifo into the unused tail with `sshp_buf_read_from_fifo()`, creates spans with `sshp_buf_span_from()`, parses frames, then drops consumed bytes with `sshp_buf_drop()`. The helpers assume the caller manages bounds and buffer lifetime.

## State And Persistence Behavior
`sshp_buf` owns no memory by itself unless initialized via `sshp_buf_alloc()`. `sshp_buf_free()` releases the backing allocation and zeroes the struct. Buffer contents are transient RX data only. `sshp_buf_drop()` preserves unconsumed bytes for the next RX iteration, allowing partial frames to persist in memory across wakeups.

## Dependencies And Integration Points
Uses kfifo, slab allocation, and `struct ssam_span` from `linux/surface_aggregator/serial_hub.h`. It is included by `ssh_packet_layer.h` and the parser implementation.

## Risks
The inline helpers are intentionally low-level. `sshp_buf_drop()` assumes `n <= buf->len`; `sshp_buf_span_from()` warns that the offset is not validated; and `sshp_buf_read_from_fifo()` trusts capacity accounting. Incorrect caller arithmetic can cause underflow or out-of-bounds spans.

## Test Signals
Exercise allocation failure, FIFO-to-buffer transfer with partial capacity, dropping zero/some/all bytes, preserving incomplete frames across drops, span creation at valid offsets, and parser behavior when the RX buffer reaches capacity.
