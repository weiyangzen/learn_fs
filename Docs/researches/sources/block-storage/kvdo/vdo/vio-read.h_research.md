# File Research: sources/block-storage/kvdo/vdo/vio-read.h

## Purpose
Declares read-path entry and cleanup functions for `data_vio`.

## Public API
- `launch_read_data_vio()`: start async read or read-modify-write processing.
- `cleanup_read_data_vio()`: release read-path logical lock and return the VIO.
