# sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4-qat.h

Purpose: C ABI declaration for QAT-flavored LZ4 batch compression/decompression hooks, modeled after LZ4 public API visibility conventions.

Important APIs/types/functions: defines `LZ4LIB_VISIBILITY`, `LZ4LIB_API`, opaque typedef `LZ4_qat_param`, empty struct `_LZ4_qat_param`, `LZ4_compress_qat`, `LZ4_decompress_qat`, `qat_init`, and `qat_uninit`.

Control flow: header only. C and C++ consumers call the functions implemented in `lz4-qat.c`.

State and persistence: the QAT parameter type is currently empty, so no accelerator state can be represented through the public type. Persistent compressed data format is still normal LZ4 block data produced by the implementation.

Dependencies/integration: included by `compressor.cpp` under `ENABLE_QAT` and by `lz4-qat.c`. Uses `extern "C"` for C++ compatibility and includes standard `stddef.h`/`stdio.h`.

Risks: API names imply hardware acceleration, but the paired implementation is a software stub. There is no destination capacity argument, forcing the implementation to make assumptions. The empty struct limits future QAT state without ABI changes if callers allocate it by value or size.

Test signals: no standalone tests; meaningful coverage requires building with `ENABLE_QAT` and exercising `LZ4Compressor::compress_batch` / `decompress_batch`.
