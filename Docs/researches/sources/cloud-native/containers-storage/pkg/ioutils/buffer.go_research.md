## sources/cloud-native/containers-storage/pkg/ioutils/buffer.go

Purpose: small fixed-capacity buffer used internally by `BytesPipe`.

Important APIs/types/functions: `errBufferFull`, `fixedBuffer`, `Write`, `Read`, `Len`, `Cap`, `Reset`, and `String`.

Control flow: writes copy into `buf[pos:cap(buf)]` without extending length, advances `pos`, and returns `errBufferFull` when capacity is exhausted. Reads copy unread bytes from `lastRead:pos`, advances `lastRead`, and never returns EOF. Reset zeroes positions and shrinks slice length to zero.

State and persistence: in-memory mutable positions and backing slice only.

Dependencies and integration points: buffer pooling in `bytespipe.go` relies on capacity and reset behavior.

Risks: because slice length remains zero while data is written into capacity, direct use of `buf` requires slicing by capacity/positions; this is intentional but non-idiomatic. `Read` returns `0, nil` at exhaustion.

Test signals: `buffer_test.go` covers capacity, length after reads, string of unread data, full writes, and reads.
