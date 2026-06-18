# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/config.c

## Purpose
`config.c` creates UDS index configurations, serializes/deserializes saved configuration metadata, validates user configuration against saved index geometry, and normalizes concurrency parameters.

## Important APIs, Types, And Functions
- Constants include magic `"ALBIC"`, versions `"06.02"` and `"08.02"`, default/max read threads, and buffer lengths.
- `uds_validate_config_contents()` reads saved config data, decodes versioned fields, handles remapping fields for 8.02, and compares to the supplied configuration.
- `uds_write_config_contents()` writes magic, version, base configuration fields, and optional remapping fields.
- `compute_memory_sizes()` maps memory-size presets and sparse mode to `chapters_per_volume`, `record_pages_per_chapter`, and `sparse_chapters_per_volume`.
- `normalize_zone_count()` and `normalize_read_threads()` clamp concurrency knobs.
- `uds_make_configuration()` allocates `struct uds_configuration`, builds index geometry, and fills derived defaults and user parameters.
- `uds_free_configuration()` and `uds_log_configuration()` handle teardown and diagnostics.

## Control Flow And Data Flow
Configuration creation starts from `uds_parameters`, computes chapter/page counts from memory size and sparse flag, allocates geometry with `uds_make_index_geometry()`, normalizes zones/readers, and records nonce, block device, offset, and size. Saved configuration validation reads magic and version, decodes the common 6.02 payload, optionally reads 8.02 remap fields into the user geometry, then compares saved and requested values field-by-field.

Writing selects the older 6.02 format for superblock versions below 4 to preserve compatibility, otherwise writes 8.02 and includes reduced-index remapping metadata.

## State And Persistence Behavior
Saved config content is persistent index metadata. It protects against opening an index with incompatible geometry, cache, sampling, mean-delta, page-size, or nonce. Version 8.02 adds fields for LVM conversion/reduced geometry remapping. Sparse configurations multiply chapter count and persistent storage footprint while preserving memory footprint.

## Dependencies And Integration Points
The file depends on logging, allocation, numeric helpers, string utilities, thread utilities, buffered readers/writers, geometry, and indexer parameter types. It is called from index layout load/save paths and index-session creation.

## Risks
- Version handling must remain compatible with older metadata; writing 8.02 to old superblock versions would break downgrade/compatibility expectations.
- `compute_memory_sizes()` has many preset branches; invalid enum values return `-EINVAL` while most UDS code expects positive UDS statuses.
- Sparse mode multiplies chapters by ten and sets 95 percent sparse chapters; geometry and storage sizing must account for this.
- Validation writes remapping fields into `user_config->geometry` before full match confirmation.

## Test Signals
Tests should cover all supported memory-size presets, sparse and reduced modes, invalid memory sizes, zone/read-thread clamping, 6.02 and 8.02 read/write round trips, nonce mismatch, page-size mismatch, remapped geometry persistence, and compatibility behavior for superblock version below 4.
