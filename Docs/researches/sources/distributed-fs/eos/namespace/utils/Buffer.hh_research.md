# sources/distributed-fs/eos/namespace/utils/Buffer.hh

## Purpose
`Buffer.hh` implements a small data buffer abstraction on top of `std::vector<char>` with optional read-only external storage mode. It is used by namespace utilities such as checksum formatting.

## Important APIs, Types, and Functions
`Buffer` constructors initialize owned vector storage or copy from another buffer. `operator=` deep-copies from the other buffer. `getDataPtr()` returns either vector data or an external pointer. `setDataPtr()` switches the buffer to external storage with explicit length. `getDataPadded()` returns zero for out-of-range reads. `getSize()`, `setSize()`, `putData()`, `grabData()`, and `getCRC32()` provide size, append, copy-out, and checksum operations.

## Control Flow
In owned mode, `putData()` resizes the vector and appends bytes; `grabData()` copies from the vector after bounds checking. In external mode, `putData()` throws `MDException(EINVAL)` because the structure is read-only, while reads and padded access use `data` and `len`. `getCRC32()` computes zlib CRC32 over `getDataPtr()` and `size()`.

## State and Persistence Behavior
The class owns data only in vector mode. External mode stores a raw pointer without owning lifetime. It has no persistence. Copy assignment resets to owned mode and copies bytes from the source's visible data.

## Dependencies and Integration Points
It depends on zlib and `MDException`. It integrates with checksum and serialization helpers that need byte buffers with padded reads for legacy checksum display.

## Risks and Edge Cases
Calling `getDataPtr()` on an empty owned vector uses `&operator[](0)`, which is undefined for truly empty vectors. `getCRC32()` uses `size()` rather than `getSize()`, so external-buffer mode may compute over the vector's size rather than `len`; this is a likely bug if CRC32 is used after `setDataPtr()`. External pointer lifetime is unmanaged and can dangle.

## Test Signals
Useful tests should cover owned append/copy, external read-only behavior, `grabData()` bounds, padded reads, empty buffers, and CRC32 in both owned and external modes.
