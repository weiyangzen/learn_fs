# sources/control-plane/mayastor/io-engine/src/core/wiper.rs

## Purpose
Implements bdev wiping and streamed wipe progress reporting for replica cleanup/test APIs. It supports no-op, write-zeroes, and CRC32C checksum modes.

## Important APIs, Types, and Functions
- `Error` maps wipe validation, I/O, abort, unsupported method, and notification failures.
- `Wiper` owns an `UntypedBdevHandle` and `WipeMethod`.
- `StreamedWiper<S: NotifyStream>` wipes in chunks and notifies clients.
- `NotifyStream` abstracts progress streaming and close detection.
- `WipeMethod::{None, WriteZeroes, Unmap, WritePattern, CkSum}` and `CkSumMethod::Crc32`.
- `WipeStats`, `FinalWipeStats`, and `WipeIterator` track progress, bandwidth logging, and chunk iteration.

## Control Flow and State
`Wiper::new` validates method support. `wipe` either does nothing, submits `write_zeroes_at`, reads and updates CRC, or returns unimplemented for unmap/pattern. `StreamedWiper::new` validates chunk size against bdev size and block length, constructs stats, and enforces max chunk count. `wipe` sends initial stats, iterates chunks, splits large chunks into 8 MiB operations, checks aborts, updates stats, finalizes CRC by XOR on the last chunk, and returns final timing.

State is in-memory progress and mutable checksum. Device contents are modified by write-zeroes.

## Dependencies and Integration Points
Used by replica gRPC and test gRPC. Depends on `UntypedBdevHandle`, SPDK CRC constants/functions, `byte_unit`, `uuid`, and `CoreError`.

## Risks and Test Signals
The iterator skips 33 backup GPT blocks at the end, which affects exact wipe size. `dma_malloc(size).unwrap()` can panic during checksum mode. Unsupported methods are represented but rejected. Tests should cover chunk alignment, zero-size devices, max chunk limits, abort on closed streams, CRC finalization, large-chunk splitting, and conversion between `Error` and `CoreError`.
