# File Research: sources/block-storage/kvdo/vdo/vio-write.h

## Purpose
Declares write-path entry points and dedupe/compression re-entry points.

## Public API
- `launch_write_data_vio()`: start async write processing.
- `cleanup_write_data_vio()`: release write-path locks and return/reuse the VIO.
- `continue_write_after_compression()`: resume write path after packer compression result.
- `launch_compress_data_vio()`: attempt compression path.
- `launch_deduplicate_data_vio()`: commit a verified duplicate mapping.
