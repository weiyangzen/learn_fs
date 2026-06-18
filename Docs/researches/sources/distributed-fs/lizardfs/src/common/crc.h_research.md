# sources/distributed-fs/lizardfs/src/common/crc.h

Purpose: declares the CRC32 public API and helper macros used by data-integrity code.

Important APIs/types/functions: `mycrc32(crc, block, leng)`, `mycrc32_combine(crc1, crc2, leng2)`, `mycrc32_init()`, `recompute_crc_if_block_empty`, and macros for zero blocks, zero-expanded blocks, and XORed block CRCs.

Control flow: the macros compose the two fundamental functions to calculate CRC effects for implicit zero data and XOR relationships without reading full buffers.

State and persistence: the header itself has no state; implementation may use static tables.

Dependencies and integration: depends on `platform.h`, integer types, and the implementation's protocol constants. It is included by chunk storage and tests.

Risks: macro arguments can be evaluated multiple times, so callers should avoid side effects. The API uses 32-bit lengths; larger buffers require chunking.

Test signals: `crc_unittest.cc` validates public functions and zero-block macro behavior.
