# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/io-factory.h

## Purpose
Declares the storage I/O abstraction used by UDS layout and volume code to access contiguous regions of a block device.

## Important APIs, Types, And Functions
Defines `UDS_BLOCK_SIZE` as 4096 and `SECTORS_PER_BLOCK`. Forward-declares `buffered_reader`, `buffered_writer`, and `io_factory`. Exposes factory creation/replacement/release, writable-size query, raw dm-bufio client creation, sequential reader creation/read/verify/free, and sequential writer creation/write/flush/free.

## Control Flow
Callers create a factory from a block device, then create dm-bufio clients or bounded buffered readers/writers for specific regions. Writers append serialized payloads and flush; readers consume serialized payloads and can verify magic bytes.

## State And Persistence
The header hides all mutable I/O cursor state. Persistence semantics are block-sized and rely on dm-bufio flushing in the implementation.

## Dependencies And Integration Points
Includes `linux/dm-bufio.h` and therefore ties indexer persistence to the device-mapper buffer I/O layer. It is included by layout, page-map, open-chapter, volume-index, and volume modules.

## Risks
All offsets are in UDS blocks, not bytes or sectors, except where callers pass higher-level configuration offsets that have already been normalized. Mixing units can place readers/writers on wrong regions.

## Test Signals
Compile coverage and integration tests should verify offset handling, block-size assumptions, and reader/writer round trips for every serialized structure.
