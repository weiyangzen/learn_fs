# Group Research: group_281_devicemapper_rs_sources_block_storage_devicemapper_rs_src_thinpoolde_48fbb8cd74b4

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/thinpooldev.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/thinpooldev.rs

This file implements the `thin-pool` device-mapper abstraction for `devicemapper-rs`. It covers target-table parameter modeling, table serialization/parsing, kernel status parsing, lifecycle management for a `ThinPoolDev`, table mutation helpers for backing metadata/data devices, feature toggles, and loopback-backed integration tests.

Core types:
- `ThinPoolTargetParams` stores metadata device, data device, data block size, low-water mark, and thin-pool feature arguments.
- `ThinPoolDevTargetTable` wraps the single target line required for a thin-pool mapping.
- `ThinPoolDev` owns the created pool and the two backing `LinearDev` devices.
- `ThinPoolUsage`, `ThinPoolWorkingStatus`, `ThinPoolStatusSummary`, `ThinPoolNoSpacePolicy`, and `ThinPoolStatus` model `dmsetup status` output.

`ThinPoolTargetParams::new` accepts feature args as a `Vec<String>` but stores them in a `HashSet<String>`, deduplicating flags and making their serialized order nondeterministic. `Display` emits `thin-pool` plus the target parameter string. `TargetParams::param_str` emits the device-mapper table parameter sequence:

`<metadata_dev> <data_dev> <data_block_size> <low_water_mark> <feature_arg_count> [feature_args...]`

`FromStr` expects the target name followed by at least metadata device, data device, block size, and low-water mark. It accepts both no feature-count field and an explicit `0` feature count. A notable robustness issue is that when a nonzero feature count is present, it slices `vals[6..6 + count]` without checking that enough fields exist. Malformed input such as a declared feature count larger than the remaining fields can panic instead of returning `DmError`. The status parser has a similar shape for metadata/data usage: it splits `used/total` strings and indexes both halves without validating that the slash-delimited field has exactly two parts.

`ThinPoolDevTargetTable::from_raw_table` enforces device-mapper’s single-line thin-pool table shape. It joins the raw target type and parameter string back into one string and delegates parsing to `ThinPoolTargetParams`. `to_raw_table` uses the project’s `to_raw_table_unique!` helper, so this type integrates with the shared target-table machinery used by other DM devices.

`ThinPoolDev` implements `DmDevice<ThinPoolDevTargetTable>`. Its `size()` returns the size of the data backing `LinearDev`. `teardown()` removes the thin-pool device first, then tears down the data device, then the metadata device. `equivalent_tables()` compares start, length, metadata device, data device, and data block size, deliberately ignoring differences such as low-water mark; the comment notes that equivalence is still stricter than ideal in some cases.

Creation and setup:
- `ThinPoolDev::new` fails if a device with the requested name already exists, builds a table from supplied metadata/data `LinearDev`s, then creates the DM device with private options.
- `ThinPoolDev::setup` is idempotent over an existing named device: if present, it reconstructs local state from `device_info` and validates with `device_match`; if absent, it creates the device.
- `gen_table` creates a one-line table starting at sector zero and using the current data device size as the target length.

The file’s public mutators support changing pool behavior and backing layout:
- `set_low_water_mark` clones the current table, updates the low-water mark, loads the new table, and updates local state. It does not resume the pool itself.
- `set_meta_table` updates and resumes the metadata `LinearDev`, then reloads the unchanged pool table.
- `set_data_table` updates and resumes the data `LinearDev`, adjusts the pool table length to the new data size, reloads it, and updates local state.
- Feature toggles are implemented by `set_feature_arg` and `unset_feature_arg`, which load the changed table, update local state, and resume the pool when a change was actually made.
- Public feature helpers map directly to kernel thin-pool flags: `error_if_no_space`, `queue_if_no_space`, `skip_block_zeroing`, `require_block_zeroing`, `no_discard_passdown`, and `discard_passdown`.

`ThinPoolStatus::from_str` parses device-mapper status output. It recognizes top-level `Error` and `Fail` lines, otherwise parses a working status with transaction id, metadata usage, data usage, held metadata root, summary state (`rw`, `ro`, `out_of_data_space`), discard passdown state, no-space policy, needs-check flag, and optional kernel 4.19+ metadata low-water field. Unknown enum-like tokens are reported through `make_unexpected_value_error`.

Tests are integration-heavy and require loopback/device-mapper support. The test helper `minimal_thinpool` carves one supplied block device into metadata and data `LinearDev`s, then creates a minimal pool with `no_discard_passdown` and `skip_block_zeroing`. Tests cover:
- creating a minimum-size pool and validating status/table fields;
- rejecting too-small data block size through kernel ioctl failure;
- extending data and metadata backing tables;
- repeated suspend/resume;
- status with `DM_NOFLUSH`;
- parsing target params with omitted and explicit zero feature-count fields.

Main risks and maintenance notes:
- Malformed table/status strings can panic through unchecked vector indexing after split/slice operations.
- Feature argument serialization from `HashSet` is nondeterministic, which is acceptable only if consumers treat feature order as semantically irrelevant.
- Data block-size validation is documented but delegated to the kernel rather than checked before ioctl.
- Several methods load tables but leave final resume responsibility to the caller, while feature toggles resume automatically; callers need to know this behavioral difference.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/thinpooldev.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/devicemapper-rs/src/units.rs -->
# File Research: sources/block-storage/devicemapper-rs/src/units.rs

This file defines strongly typed unit wrappers and conversions used throughout `devicemapper-rs`, especially by cache and thin-pool code. It prevents mixing bytes, 512-byte sectors, metadata blocks, and data blocks in function signatures and arithmetic.

Constants:
- `SECTOR_SIZE` is `512` bytes.
- `META_BLOCK_SIZE` is `Sectors(8)`, matching the kernel device-mapper metadata block size of 4096 bytes.
- `MAX_META_DEV_SIZE` encodes the kernel metadata maximum block count, but is currently `dead_code` and used only as documentation/local reference.

Unit types are generated by project macros:
- `DataBlocks` is a `u64`-backed range type for pool/cache data blocks.
- `MetaBlocks` is a `u64`-backed range type for device-mapper metadata blocks.
- `Bytes` is a `u128`-backed range type for byte counts.
- `Sectors` is a `u64`-backed range type for 512-byte sectors.

Conversions:
- `MetaBlocks::sectors()` multiplies metadata block count by `META_BLOCK_SIZE`, returning `Sectors`.
- `Bytes::sectors()` returns the number of whole sectors contained in the byte count by integer division.
- `Sectors::bytes()` converts sectors to bytes using `u128` multiplication to avoid overflowing during the sector-to-byte conversion.
- `Sectors::metablocks()` returns the number of whole metadata blocks contained in the sector count.

The tests focus on overflow boundary behavior:
- `test_large` verifies that `Sectors(u64::MAX).bytes().sectors()` round-trips.
- `test_too_large` constructs one sector more than `u64::MAX` sectors in bytes, converts back to sectors, and expects wrap/truncation to `Sectors(0)` because `Bytes::sectors()` casts the `u128` quotient to `u64`.

Main risks and maintenance notes:
- `Bytes::sectors()` silently truncates to `u64` after division. The test documents this wraparound behavior, but callers that convert arbitrary large byte counts can receive a small sector count instead of an error.
- Conversions intentionally floor partial sectors/metablocks; this is correct for “whole units contained” semantics but must not be reused where rounding up is required for allocation sizing.
- `MAX_META_DEV_SIZE` duplicates a kernel-derived limit but is private and unused in production code, so runtime validation elsewhere does not rely on it.
<!-- END FILE RESEARCH: sources/block-storage/devicemapper-rs/src/units.rs -->