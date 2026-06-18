# File Research: sources/cow-pools/bcachefs-tools/linux/zstd_decompress_module.c

## Purpose
Linux zstd decompression/common API wrapper over upstream zstd.

## Key APIs
- `zstd_is_error()`, `zstd_get_error_code()`, `zstd_get_error_name()`
- `zstd_dctx_workspace_bound()`, `zstd_init_dctx()`, `zstd_decompress_dctx()`
- `zstd_dstream_workspace_bound()`, `zstd_init_dstream()`
- `zstd_reset_dstream()`, `zstd_decompress_stream()`
- `zstd_find_frame_compressed_size()`, `zstd_get_frame_header()`

## Implementation Notes
- Static decompression contexts are created from caller workspaces.
- `max_window_size` is accepted for API compatibility but ignored by `zstd_init_dstream()` in this wrapper.

## Dependencies
Uses `linux/zstd.h` and exports Linux-compatible symbols.
