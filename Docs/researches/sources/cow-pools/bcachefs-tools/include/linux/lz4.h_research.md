# File Research: sources/cow-pools/bcachefs-tools/include/linux/lz4.h

This header adapts the system `<lz4.h>` API to kernel-style names. `LZ4_compress_destSize()` drops the workspace argument and calls the library function.

High-compression `LZ4_compress_HC()` is stubbed to `-1`, and workspace-size constants are set to `0`. Code requiring real HC compression must not rely on this shim.
