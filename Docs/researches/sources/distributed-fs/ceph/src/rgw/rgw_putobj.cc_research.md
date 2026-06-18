# sources/distributed-fs/ceph/src/rgw/rgw_putobj.cc

## Purpose

Implements data-processor pipeline components for object PUT paths. The processors reshape incoming byte streams into fixed-size chunks or stripe-relative writes before forwarding them to the next SAL `DataProcessor`.

## Important APIs, Types, and Functions

`ChunkProcessor::process()` buffers partial input until `chunk_size` bytes are available, forwards full chunks, and flushes leftover bytes on an empty-buffer call. `StripeProcessor::process()` forwards data within current stripe bounds, flushes the downstream processor at stripe boundaries, asks a `StripeGenerator` for the next stripe size, and rewrites offsets to be relative to each stripe.

## Control Flow and Data Flow

Chunk processing asserts that the caller's absolute offset has not moved behind buffered data, computes the first downstream position as `offset - chunk.length()`, appends input to the leftover buffer, then repeatedly splices and forwards full chunks. A zero-length input is a flush signal: any leftover chunk is forwarded at its computed position, then an empty flush is passed downstream at the caller's offset.

Stripe processing asserts the offset is inside or after the current stripe start. If input exceeds the current stripe's remaining bytes, it forwards the partial slice, sends an empty flush at the stripe-relative end, asks the generator for a new stripe, updates bounds, and continues. Remaining data that fits in the current stripe is forwarded without flushing.

## State and Persistence Behavior

The file owns only transient in-memory pipeline state: `ChunkProcessor::chunk` leftovers and `StripeProcessor::bounds`. It does not persist metadata or object data itself; persistence happens in the downstream processor.

## Dependencies and Integration Points

Depends on `bufferlist`, `rgw_putobj.h`, and SAL `DataProcessor`. It integrates with RGW PUT/copy/multipart upload code that builds processor chains for object layout, compression, encryption, or RADOS writes.

## Risks and Edge Cases

Zero-length buffers are control messages, so callers must not use them as ordinary data. `chunk_size` and generated stripe sizes must be nonzero; stripe code asserts the generated size but chunk code would loop forever if constructed with zero. Offset correctness is critical because downstream processors receive chunk- or stripe-relative positions.

## Test Signals

Test exact chunk boundaries, partial chunks followed by flush, multiple chunks in one call, stripe crossing with multiple generated stripes, empty flush propagation, downstream error propagation, and assertions/guard behavior for zero sizes or non-monotonic offsets.
