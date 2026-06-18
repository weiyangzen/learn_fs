# File Research: sources/block-storage/kvdo/vdo/super-block-codec.c

This file encodes and decodes the VDO super block sector payload. The fixed format is header plus component data plus CRC32 checksum; the whole encoding is constrained to the first sector to reduce torn-write corruption risk even though the backing allocation is a full VDO block.

Key behavior:
- `vdo_initialize_super_block_codec()` creates a component buffer, full-block encoded buffer, and sector-sized block buffer wrapper.
- `vdo_encode_super_block()` resets the block buffer, writes header version `12.0`, copies pre-encoded component data, computes CRC32 over encoded bytes so far, and appends the checksum.
- `vdo_decode_super_block()` decodes/validates the header, restricts the buffer to the declared payload size, copies component data except checksum into `component_buffer`, computes CRC, reads saved checksum, verifies all payload bytes were consumed, and returns `VDO_CHECKSUM_MISMATCH` on mismatch.

The codec depends on buffer primitives, `header` validation, constants such as `VDO_SECTOR_SIZE`, and CRC support from VDO.
