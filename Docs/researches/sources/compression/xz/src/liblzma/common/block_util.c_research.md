# sources/compression/xz/src/liblzma/common/block_util.c

Purpose: utility functions for deriving and validating XZ Block compressed, unpadded, and total sizes.

Important APIs/types/functions: public `lzma_block_compressed_size(lzma_block *block, lzma_vli unpadded_size)`, `lzma_block_unpadded_size(const lzma_block *block)`, and `lzma_block_total_size(const lzma_block *block)`.

Control flow: `lzma_block_compressed_size()` validates known unpadded size, header size, and check size, subtracts header/check to derive compressed size, rejects zero/invalid values, and stores it to `block`. `lzma_block_unpadded_size()` validates version, header size, check type, and compressed size, then returns header + compressed + check unless it would exceed VLI limits or padding constraints. `lzma_block_total_size()` rounds unpadded size up to a four-byte boundary.

State and persistence: only `lzma_block_compressed_size()` mutates `block->compressed_size`; others are pure calculations.

Dependencies/integration: includes `common.h` and `index.h`; uses check sizes, VLI validation, and Index padding/size rules. Used by header encoder/decoder and Index construction.

Risks: size arithmetic prevents overflow and malformed Block acceptance. Misinterpreting padded vs unpadded sizes breaks Index validation. Unknown sizes must be handled without treating `LZMA_VLI_UNKNOWN` as a normal value.

Test signals: `test_block_header`, Index tests, and boundary cases for zero compressed size, maximum VLI sizes, check sizes, and total-size padding.
