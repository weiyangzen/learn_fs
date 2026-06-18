# sources/distributed-fs/lizardfs/src/common/crc_unittest.cc

Purpose: GoogleTest coverage for LizardFS CRC32 and CRC combination semantics.

Important APIs/types/functions: tests call `mycrc32`, `mycrc32_zeroblock`, and `mycrc32_combine` using fixed strings and `MFSBLOCKSIZE` buffers.

Control flow: `MyCrc32` compares several repeated-`a` strings to known external CRC32 values. `MfsCrc32Zeroblock` compares explicit zero-buffer CRC to the macro. `MyCrc32Combine` splits a full block at powers-of-two-related offsets and verifies combined CRC equals whole-buffer CRC.

State and persistence: test-only vectors and strings.

Dependencies and integration: includes `common/crc.h`, `protocol/MFSCommunication.h`, and `gtest`.

Risks: tests assume CRC is enabled or fake implementation is configured consistently; fake CRC would make known-value tests fail unless test selection changes. Coverage does not test `recompute_crc_if_block_empty` directly.

Test signals: strong signal for normal and concatenate CRC correctness over block-sized data.
