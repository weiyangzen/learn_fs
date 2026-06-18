<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/block_xor.h -->
# sources/distributed-fs/lizardfs/src/common/block_xor.h

## Purpose

This header declares the common in-place XOR primitive used by chunk/parity code.

## Important APIs, Types, and Functions

It declares `void blockXor(uint8_t* dest, const uint8_t* source, size_t size)`.

## Control Flow

No control flow is present in the header. Callers provide destination, source, and byte count; implementation selects aligned or unaligned processing.

## State and Persistence Behavior

The API mutates the destination buffer only.

## Dependencies and Integration Points

It includes platform and integer headers. It is a low-level dependency for erasure/parity reconstruction.

## Risks and Edge Cases

The contract does not specify null handling for zero size, overlap behavior, or alignment requirements. Callers should provide valid byte ranges.

## Test Signals

Expected tests compare output bytes for varied alignments, zero length, and large block sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/block_xor.h -->
