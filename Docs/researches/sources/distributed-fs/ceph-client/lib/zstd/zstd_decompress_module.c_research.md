# sources/distributed-fs/ceph-client/lib/zstd/zstd_decompress_module.c

## Purpose
`zstd_decompress_module.c` is the Linux kernel export wrapper for Zstd decompression. It exposes stable `zstd_*` names for error inspection, decompression contexts, DDicts, one-shot decompression, streaming decompression, frame size lookup, and frame header parsing.

## Important APIs, types, and functions
Exported symbols include `zstd_is_error`, `zstd_get_error_code`, `zstd_get_error_name`, `zstd_dctx_workspace_bound`, `zstd_create_dctx_advanced`, `zstd_free_dctx`, `zstd_create_ddict_byreference`, `zstd_free_ddict`, `zstd_init_dctx`, `zstd_decompress_dctx`, `zstd_decompress_using_ddict`, `zstd_dstream_workspace_bound`, `zstd_init_dstream`, `zstd_reset_dstream`, `zstd_decompress_stream`, `zstd_find_frame_compressed_size`, and `zstd_get_frame_header`.

## Control flow
Wrappers mainly forward to upstream `ZSTD_*` functions. Static initialization rejects a NULL workspace. `zstd_init_dstream` accepts `max_window_size` for the Linux API but discards it before calling `ZSTD_initStaticDStream`, while workspace sizing still uses the max-window parameter.

## State and persistence
Runtime state is in `zstd_dctx`, `zstd_dstream`, and `zstd_ddict` instances. DDicts created by reference depend on the caller keeping dictionary bytes alive. The module itself has no global mutable decompression state.

## Dependencies and integration points
It includes Linux kernel/module/string headers, `<linux/zstd.h>`, and Zstd deps. It integrates with kernel consumers that need decompression without directly depending on upstream symbol names, and with the common module for shared error helpers.

## Risks and test signals
Risks include by-reference dictionary lifetime errors, static workspace sizing mismatches, ignored `max_window_size` surprises at init, and callers failing to check `size_t` error returns. Test signals include frame and streaming decompression, malformed input, DDict reuse, reset behavior, workspace-bound allocation tests, and exported-symbol availability.
