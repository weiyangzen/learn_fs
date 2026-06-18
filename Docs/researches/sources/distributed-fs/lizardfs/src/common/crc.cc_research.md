# sources/distributed-fs/lizardfs/src/common/crc.cc

Purpose: provides LizardFS CRC32 calculation, CRC concatenation, initialization, and empty-block CRC repair.

Important APIs/types/functions: `mycrc32`, `mycrc32_combine`, `mycrc32_init`, legacy table generators `crc_generate_main_tables` and `crc_generate_combine_tables`, and `recompute_crc_if_block_empty`.

Control flow: build-time branches select a fake CRC implementation when `ENABLE_CRC` is off, `crcutil::GenericCrc` when available, or legacy endian-aware table code otherwise. The legacy implementation aligns byte input, processes 32-byte and 4-byte chunks through precomputed tables, and uses GF(2) matrix-derived combine tables to concatenate CRCs. `recompute_crc_if_block_empty` checks for zero CRC and all-zero `MFSBLOCKSIZE` block before assigning the cached zero-block CRC.

State and persistence: legacy mode has static CRC tables and a static cached empty-block CRC. No persistence or synchronization; callers must ensure initialization where required.

Dependencies and integration: depends on `crc.h`, `protocol/MFSCommunication.h` for `CRC_POLY` and `MFSBLOCKSIZE`, optional `generic_crc.h`, and endian macros. It underpins block integrity and chunk verification.

Risks: fake CRC mode can mask corruption and must be build-controlled. The all-zero check uses `memcmp(block, block + 1, MFSBLOCKSIZE - 1)` and assumes the full block buffer is readable. Static initialization of `emptyBlockCrc` calls combine macros after `mycrc32_init` should have run in legacy mode.

Test signals: `crc_unittest.cc` covers known CRC values, zero block equivalence, and combine behavior across multiple tail lengths.
