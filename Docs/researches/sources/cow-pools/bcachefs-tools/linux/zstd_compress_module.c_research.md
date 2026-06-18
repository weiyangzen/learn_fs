# File Research: sources/cow-pools/bcachefs-tools/linux/zstd_compress_module.c

## Purpose
Linux zstd compression API wrapper over the upstream/new zstd API.

## Key APIs
- `zstd_min_clevel()`, `zstd_max_clevel()`
- `zstd_compress_bound()`
- `zstd_get_params()`
- `zstd_cctx_workspace_bound()`, `zstd_init_cctx()`, `zstd_compress_cctx()`
- `zstd_cstream_workspace_bound()`, `zstd_init_cstream()`
- `zstd_reset_cstream()`, `zstd_compress_stream()`, `zstd_flush_stream()`, `zstd_end_stream()`

## Implementation Notes
- `zstd_cctx_init()` resets the context, sets pledged source size, then maps Linux zstd parameter structs to `ZSTD_CCtx_setParameter()`.
- `pledged_src_size == 0` is translated to `ZSTD_CONTENTSIZE_UNKNOWN` for stream init.
- Static contexts are initialized from caller-provided workspaces.

## Dependencies
Uses `linux/zstd.h` and exports Linux-compatible symbols.
