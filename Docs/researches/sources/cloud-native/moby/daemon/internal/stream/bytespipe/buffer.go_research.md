# sources/cloud-native/moby/daemon/internal/stream/bytespipe/buffer.go

## Purpose
Provides the fixed-size buffer primitive used by `BytesPipe`. It stores one run of bytes in a preallocated slice capacity and tracks unread data without reallocating.

## Important APIs, Types, And Functions
`fixedBuffer` contains `buf`, write position `pos`, and read position `lastRead`. `Write` copies into `buf[pos:cap(buf)]` and returns `errBufferFull` when the capacity is exhausted. `Read` copies unread bytes to the caller and advances `lastRead`. `Len`, `Cap`, `Reset`, and `String` expose unread length, capacity, reset-for-pool behavior, and unread content.

## Control Flow
Writes grow only the logical positions, not the slice length. Reads consume bytes monotonically. `Reset` clears positions and shortens the slice to length zero so pooled buffers can be reused cleanly.

## State And Persistence
The object is mutable and intentionally not synchronized; `BytesPipe` owns synchronization. No persistence exists.

## Dependencies And Integration Points
Used by `bytespipe.go` as the RLE-like chunk storage unit behind a blocking pipe. The sentinel `errBufferFull` is an expected internal control-flow result.

## Risks And Test Signals
The implementation never compacts read space for later writes; once capacity is consumed the buffer is full even if earlier bytes were read. Tests validate capacity, unread length, stringing unread data, full-buffer errors, and sequential reads.
