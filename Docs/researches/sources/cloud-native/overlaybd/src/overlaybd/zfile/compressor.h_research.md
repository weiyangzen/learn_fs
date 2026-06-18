# sources/cloud-native/overlaybd/src/overlaybd/zfile/compressor.h

Purpose: public compression interface and option layout for zfile blocks.

Important APIs/types/functions: `CompressOptions` defines algorithm IDs `MINI_LZO`, `LZ4`, `ZSTD`, default block size, algorithm, level, dictionary flags, reserved fields, dictionary size, verify flag, and padding; its size is asserted to 24 bytes. `CompressArgs` carries optional dictionary file/buffer, options, header-overwrite flag, and worker count. `ICompressor` defines single and batch compress/decompress APIs plus `nbatch`. `create_compressor` is an `extern "C"` factory.

Control flow: callers construct options/args, request a compressor from `create_compressor`, then call single-block or batch APIs. The header does not implement behavior.

State and persistence: `CompressOptions` is explicitly described as written into files, so its field order and size are persistent format data. `CompressArgs` is transient runtime configuration. `ICompressor` implementations hold runtime buffers/state.

Dependencies/integration: used by `compressor.cpp` and zfile format implementation. References Photon `IFile` only by forward declaration to avoid pulling full filesystem headers into consumers.

Risks: changing `CompressOptions` layout breaks stored zfile headers. Dictionary fields are present but not substantively implemented in the compressor body in this subset. `MINI_LZO` remains an option ID but factory support is absent. Ownership of raw `dict_buf` is transferred into `unique_ptr`, so callers must not free it afterward.

Test signals: compile-time size assertion is the direct guard; runtime round-trip tests should cover option combinations, algorithm IDs, and header compatibility.
