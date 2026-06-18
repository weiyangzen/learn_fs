# sources/cloud-native/overlaybd/src/overlaybd/zfile/lz4/lz4-qat.c

Purpose: placeholder QAT-flavored LZ4 batch API implementation that currently delegates to normal LZ4 software routines.

Important APIs/types/functions: global `gDebugParam`, `qat_init`, `qat_uninit`, `LZ4_compress_qat`, and `LZ4_decompress_qat`.

Control flow: init/uninit return success without configuring state. Compress/decompress loop over `n` chunks and call `LZ4_compress_default` or `LZ4_decompress_safe` for each chunk, storing per-chunk output lengths, then return zero status.

State and persistence: no meaningful QAT state is stored; `LZ4_qat_param` is opaque and empty in the header. The functions write caller-provided destination buffers but do not persist data.

Dependencies/integration: compiled into `zfile_lib` with the bundled LZ4 sources. Called by `LZ4Compressor` only when `ENABLE_QAT` and QAT detection are active.

Risks: destination capacity is hard-coded as 4096 for every chunk instead of receiving a capacity parameter, so it is only safe when caller slot size is exactly 4096 and compressed output fits. Return value is always zero even if per-chunk LZ4 calls fail, leaving errors visible only through chunk lengths. It is not a real QAT implementation despite QAT naming.

Test signals: no direct tests in this subset. QAT-enabled compression tests should verify chunk lengths, failure propagation, and non-4096 block sizes.
