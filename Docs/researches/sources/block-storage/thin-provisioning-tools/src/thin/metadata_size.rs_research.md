# File Research: sources/block-storage/thin-provisioning-tools/src/thin/metadata_size.rs

This file estimates required thin metadata size.

Key elements:
- `MIN_DATA_BLOCK_SIZE` is 64 KiB.
- `MAX_DATA_BLOCK_SIZE` is 1 GiB.
- `ThinMetadataSizeOptions` carries `nr_blocks` and `max_thins`.
- `check_data_block_size()` validates nonzero, multiple-of-64-KiB block size and maximum size.
- `metadata_size()` estimates bytes by:
  - taking half of max mapping leaf capacity as assumed residency
  - computing mapping leaf count with `div_up`
  - adding one superblock and one root per max thin
  - capping metadata blocks at `MAX_METADATA_BLOCKS`
  - multiplying by metadata `BLOCK_SIZE`

Interactions:
- Uses `calc_max_entries::<BlockTime>()` to estimate mapping entries per node.

Risks and notes:
- This is an estimate, not an exact allocator simulation.
- `ThinMetadataSizeOptions` uses `nr_blocks`, but data block size validation is separate.
