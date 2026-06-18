# sources/distributed-fs/ceph-client/drivers/crypto/intel/iaa/iaa_crypto_comp_fixed.c Research

## Purpose
`iaa_crypto_comp_fixed.c` defines the static fixed-Huffman DEFLATE tables used by Intel IAA hardware and registers the `"fixed"` compression mode with the IAA crypto core.

## Important APIs, Types, and Functions
`fixed_ll_sym[286]` and `fixed_d_sym[30]` encode the RFC1951 fixed Huffman literal/length and distance tables in the format expected by IAA AECS compression state. `init_fixed_mode()` initializes per-device AECS state by clearing CRC/checksum fields, writing a fixed-block header (`FIXED_HDR | bfinal`) into `output_accum`, and setting `num_output_accum_bits` to `FIXED_HDR_SIZE`.

`iaa_aecs_init_fixed()` calls `add_iaa_compression_mode("fixed", ...)` with the fixed tables and init callback. `iaa_aecs_cleanup_fixed()` removes that mode through `remove_iaa_compression_mode("fixed")`.

## Control Flow
Module init in `iaa_crypto_main.c` calls `iaa_aecs_init_fixed()` before registering the IDXD subdriver. Later, each probed IAA device copies the global fixed tables into a DMA-coherent per-device `aecs_comp_table_record` and calls `init_fixed_mode()`. Module cleanup calls `iaa_aecs_cleanup_fixed()` after unregistering the IDXD driver.

## State and Persistence
The static tables are read-only kernel data. The registered compression mode persists globally while the module is loaded and no IAA devices are active during add/remove. Per-device copies are allocated and freed by main driver code.

## Dependencies and Integration Points
The file includes `idxd.h` and `iaa_crypto.h` for AECS structures, mode registration APIs, and constants. It is required by `iaa_crypto_main.c` because the exposed acomp algorithm uses `IAA_MODE_FIXED`.

## Risks and Edge Cases
The table values are hardware-specific and not self-validating. Any transcription error would produce invalid compressed output or verification failures. `init_fixed_mode()` assumes `num_output_accum_bits` is initially zeroed by the allocator before computing the byte offset. Mode registration must happen before devices are added, matching the lock/order restrictions in `add_iaa_compression_mode()`.

## Test Signals
Compression known-answer tests should verify fixed-Huffman DEFLATE output can be decompressed by generic deflate. Compression verification mode should catch CRC or table mistakes. Module load/unload tests should confirm fixed mode registration and removal succeed with no active devices.
