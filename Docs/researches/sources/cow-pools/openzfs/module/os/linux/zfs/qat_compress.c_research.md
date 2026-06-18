# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/qat_compress.c

## Purpose

Implements Intel QAT accelerated compression and decompression for ZFS buffers.

## Main State

- `dc_inst_handles`: QAT data-compression instance handles.
- `session_handles`: one compression session per instance.
- `buffer_array`: intermediate buffers required by QAT.
- `num_inst`: active instance count.
- `inst_num`: round-robin counter.
- `qat_dc_init_done`: initialization flag.
- `zfs_qat_compress_disable`: module parameter controlling use.

## Eligibility

- `qat_dc_use_accel(s_len)`: true only when compression is enabled, initialized, and buffer size is within QAT min/max bounds.

## Initialization And Cleanup

- `qat_dc_init()`: discovers QAT compression instances, caps them to `QAT_DC_MAX_INSTANCES`, sets address translation, allocates metadata/intermediate buffers, starts instances, creates DEFLATE/Adler32 stateless sessions, and marks initialization complete.
- `qat_dc_clean()`: stops instances, frees sessions and intermediate buffers, resets state.
- `qat_dc_fini()`: calls cleanup if initialized.
- `qat_dc_callback()`: completion callback for async QAT requests.

## Compression Path

- `qat_compress_impl()`: common implementation for compression and decompression.
  - Builds QAT source and destination `CpaBufferList` objects over page-mapped source, destination, and optional scratch buffers.
  - For compression:
    - Generates zlib header.
    - Submits `cpaDcCompressData`.
    - Waits for completion.
    - Checks output fits destination.
    - Writes Adler32 footer.
    - Returns compressed length.
  - For decompression:
    - Skips zlib header in source.
    - Submits `cpaDcDecompressData`.
    - Waits for completion.
    - Verifies Adler32 checksum.
    - Returns decompressed length.
  - Cleans up page mappings, metadata, and buffer lists on all paths.

- `qat_compress()`: public entry point. Allocates an additional destination-sized scratch buffer during compression so incompressible data does not cause QAT buffer-overflow warnings.

## Parameter Hook

- `param_set_qat_compress()`: changing disable flag to `0` attempts QAT DC initialization; on failure it restores disabled state.

## Notes

The implementation tracks kstats for request counts, byte totals, and failures. `CPA_STATUS_INCOMPRESSIBLE` is treated separately from hard failures.
