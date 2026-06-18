# File Research: sources/block-storage/kvdo/vdo/compression-state.h

## Purpose
Declares the compression-path state model and public helpers for `data_vio` compression eligibility, packer blocking, completion, and cancellation.

## Key Types
- `enum vio_compression_status`
  - `VIO_PRE_COMPRESSOR`
  - `VIO_COMPRESSING`
  - `VIO_PACKING`
  - `VIO_POST_PACKER`
- `struct vio_compression_state`
  - `status`
  - `may_not_compress`

## Public API
- `get_vio_compression_state()`
- `may_compress_data_vio()`
- `may_pack_data_vio()`
- `may_vio_block_in_packer()`
- `may_write_compressed_data_vio()`
- `set_vio_compression_done()`
- `cancel_vio_compression()`

## Important Invariant
The order of `enum vio_compression_status` is semantic: `advance_status()` in `compression-state.c` increments the status to move along the compression path.
