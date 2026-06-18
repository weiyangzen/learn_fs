# sources/cloud-native/ostree/src/libostree/ostree-varint.c

## Purpose
Provides internal unsigned 64-bit varint encoding and decoding helpers derived from protocol-buffer varint logic for compact binary metadata formats.

## Important APIs, Types, And Functions
`_ostree_read_varuint64(buf, buflen, out_value, bytes_read)` decodes up to ten bytes into a `guint64`. `_ostree_write_varuint64(buf, n)` appends the varint representation of `n` to a `GString`. `max_varint_bytes` is fixed at 10, the maximum for 64-bit varints.

## Control Flow
Decoding loops byte by byte, stops when the high continuation bit is clear, returns false if the buffer ends or exceeds 10 bytes, and writes the decoded value and byte count on success. Encoding splits the input into 32-bit chunks, chooses an output size through a hardcoded decision tree, fills a 10-byte temporary array through fallthrough labels, clears the continuation bit on the last byte, and appends the chosen bytes.

## State And Persistence Behavior
The functions are stateless. Encoded bytes may be persisted by callers in repository or delta metadata, so compatibility of the varint representation matters.

## Dependencies And Integration Points
Depends on GLib `GString` and integer types. It is internal to libostree metadata encoding/decoding paths.

## Risks
Malformed varints return `FALSE` without distinguishing truncated from overlong encodings. The writer intentionally uses fallthrough labels, so compiler warnings or refactors must preserve ordering. The functions encode unsigned values only; signed callers need separate zigzag or other handling.

## Test Signals
Round-trip tests for boundary values, small numbers, 2/3/4/5/8/9/10-byte encodings, truncated buffers, all-continuation malformed buffers, and maximum `G_MAXUINT64` are the strongest signals.
