# File Research: sources/block-storage/kvdo/vdo/compression-state.c

## Purpose
Implements the atomic state machine controlling whether a `data_vio` may move through VDO compression, packing, and compressed-write emission.

## Main Concepts
- Compression state is stored in `data_vio->compression.state` as an atomic `uint32_t`.
- Low byte stores `enum vio_compression_status`.
- High bit `MAY_NOT_COMPRESS_MASK` records cancellation or disallowance.
- State transitions use `atomic_cmpxchg()` with explicit memory barriers.

## Key Functions
- `get_vio_compression_state()` reads and unpacks the atomic state.
- `set_vio_compression_state()` performs compare-and-swap transition.
- `advance_status()` moves through `PRE_COMPRESSOR -> COMPRESSING -> PACKING -> POST_PACKER`, or skips to post-packer if canceled.
- `may_compress_data_vio()` rejects compression when there is no allocation, FUA is required, compression is off, no hash lock exists, or a partial discard must complete quickly.
- `may_pack_data_vio()` rejects non-compressible data, disabled compression, or canceled VIOs.
- `may_vio_block_in_packer()` advances to `VIO_PACKING`.
- `may_write_compressed_data_vio()` advances past packer and checks cancellation.
- `set_vio_compression_done()` forces `VIO_POST_PACKER` and marks `may_not_compress`.
- `cancel_vio_compression()` sets `may_not_compress` and reports whether the caller canceled a VIO currently in packer.

## Dependencies
Uses `data-vio.h` helpers for allocation/FUA checks, `vdo_get_compressing()`, and packer/dedupe interactions through the cancellation contract.

## Concurrency Notes
The state is lock-free and may be changed by multiple threads. CAS retry loops are used wherever another thread can advance or cancel the compression path concurrently.

## Research Notes
This file is central to preventing indefinite waits when a VIO is blocked in the packer while another VIO needs its logical/hash lock.
