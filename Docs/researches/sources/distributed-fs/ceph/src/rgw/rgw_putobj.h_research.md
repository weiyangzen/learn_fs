# sources/distributed-fs/ceph/src/rgw/rgw_putobj.h

## Purpose

Declares composable object PUT data processors used to transform upload streams before final storage. It provides a minimal pipe abstraction, a fixed-chunk processor, and a stripe-boundary processor.

## Important APIs, Types, and Functions

`Pipe` derives from `rgw::sal::DataProcessor` and forwards `process(bufferlist&&, uint64_t)` to a next processor. `ChunkProcessor` adds a fixed `chunk_size` and leftover `bufferlist`. `StripeGenerator` is the callback interface that returns the next stripe size for a given absolute offset. `StripeProcessor` holds a generator and current `[first, second)` stripe bounds.

## Control Flow and Data Flow

The header establishes that processors are chained by raw `DataProcessor*` pointers and that `process()` owns the moved bufferlist. `ChunkProcessor` normalizes variable input into chunks. `StripeProcessor` normalizes absolute upload offsets into stripe-local offsets and resets downstream state between stripes using empty-buffer flush calls.

## State and Persistence Behavior

No durable state is declared. Runtime state is limited to retained chunk bytes and current stripe bounds. The raw pointer ownership model implies the chain owner is responsible for processor lifetimes.

## Dependencies and Integration Points

Depends on `include/buffer.h` and `rgw_sal.h`. The API plugs into SAL object write paths and layout-specific processors.

## Risks and Edge Cases

The classes do not validate `chunk_size`, `first_stripe_size`, `next`, or `gen`; invalid construction can cause null dereferences, asserts, or infinite loops. Because empty buffers mean flush, callers must preserve that convention throughout the chain. Raw pointers make lifetime tests important.

## Test Signals

Compile-time coverage should ensure derived processors override SAL correctly. Unit tests should use fake downstream processors/generators to verify forwarded offsets, flush counts, ownership of moved bufferlists, and behavior at boundary sizes.
