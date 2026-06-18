# sources/cloud-native/overlaybd/src/overlaybd/zfile/compressor.cpp

Purpose: implementation of zfile compression/decompression backends for LZ4 and ZSTD, with optional QAT batch path for LZ4.

Important APIs/types/functions: `BaseCompressor` implements common buffer layout, `compress`, `decompress`, `compress_batch`, and `decompress_batch`. `LZ4Compressor` implements LZ4 init, optional QAT detection/init, batch size, compression, and decompression. `Compressor_zstd` implements ZSTD compression/decompression. `create_compressor` is the exported factory.

Control flow: factory switches on `CompressOptions::algo`, allocates a compressor, and calls `init`. Base init records block size and resizes per-batch pointer vectors. Batch methods divide the destination buffer into equal slots, set source/destination pointer vectors, validate per-slot capacity, and call algorithm-specific `do_*` methods. LZ4 defaults to `LZ4_compress_default` / `LZ4_decompress_safe`; ZSTD uses `ZSTD_compress` at level 3 and `ZSTD_decompress`.

State and persistence: compressor instances retain block size, maximum destination size, per-batch pointer vectors, and optional QAT state. They do not persist compressed data themselves; callers provide buffers and store results in zfile objects.

Dependencies/integration: used by zfile read/write code through `ICompressor`. Depends on bundled LZ4, libzstd, Photon logging, Photon filesystem declarations, and optional libpci/QAT shim. Build flags are controlled by zfile CMake.

Risks: the `ENABLE_QAT` LZ4 path appears stale: it references `raw_data` and `n` symbols that are not present in the current function scope, so QAT builds may fail. ZSTD `do_decompress` appears to pass `uncompressed_data` as input and `compressed_data` as output, reversed from the base pointer setup, which would break batch ZSTD decompression. Capacity checks assume equal destination slots and require `dst_buffer_capacity / n >= max_dst_size` even when chunks vary. `CompressArgs::workers` is not used here.

Test signals: zfile tests outside this subset should validate round trips. This subset's CMake indicates zfile tests are enabled under `BUILD_TESTING`; QAT and batch ZSTD paths need targeted tests because normal single-block LZ4/ZSTD paths may not cover them.
