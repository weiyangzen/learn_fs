# sources/cloud-native/moby/daemon/internal/stream/bytespipe/buffer_test.go

## Purpose
Unit-tests `fixedBuffer`, the low-level storage block used by `BytesPipe`, with attention to capacity, unread length, short writes, reset behavior, and read offsets.

## Important APIs, Types, And Functions
Tests cover `Cap`, `Len`, `String`, `Write`, `Read`, and the `errBufferFull` sentinel. They construct buffers with explicit capacities and use byte slices and strings to verify exact contents.

## Control Flow
The suite writes small strings, reads partial data, attempts writes after capacity is exhausted, resets the buffer, and reads across multiple calls. The `TestFixedBufferWrite` case confirms that a second oversized write copies only the remaining capacity and returns `errBufferFull`.

## State And Persistence
Only in-memory buffers are used. Tests inspect internal fields such as `buf.buf[:5]`, so they are tightly coupled to representation.

## Dependencies And Integration Points
Uses Go's standard testing package plus `bytes` and `errors`. These tests protect `BytesPipe` assumptions about one-way consumption and full-buffer signaling.

## Risks And Test Signals
Tests do not exercise concurrency because `fixedBuffer` is intentionally unsynchronized. The strongest signals are preserving unread-only `String`, not reusing consumed capacity before `Reset`, and returning the exact number of bytes copied before capacity exhaustion.
