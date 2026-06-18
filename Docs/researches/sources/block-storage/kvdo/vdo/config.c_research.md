# File Research: sources/block-storage/kvdo/vdo/config.c

## Purpose
Builds, serializes, deserializes, validates, and logs UDS index configuration used by VDO deduplication.

## On-Disk Format
- Magic: `"ALBIC"`
- Supported versions:
  - `"06.02"`: legacy layout without remapped virtual/physical chapter fields.
  - `"08.02"`: includes remapped chapter fields.
- Encoding and decoding use little-endian buffer helpers.

## Key Functions
- `decode_index_config_06_02()` and `decode_index_config_08_02()` parse saved config payloads.
- `read_version()` reads version bytes and dispatches to the correct decoder.
- `are_matching_configurations()` compares saved config against the runtime `struct configuration`.
- `validate_config_contents()` verifies magic, reads saved config, validates it, and imports remapped chapter metadata.
- `encode_index_config_06_02()` and `encode_index_config_08_02()` serialize runtime config.
- `write_config_contents()` writes magic, version, and serialized payload; versions below 4 use `06.02`.
- `compute_memory_sizes()` maps UDS memory configuration and sparse mode to chapter counts and record-page sizing.
- `normalize_zone_count()` defaults to half CPU cores and clamps to `[1, MAX_ZONES]`.
- `normalize_read_threads()` clamps to `[1, MAX_VOLUME_READ_THREADS]` with default 2.
- `make_configuration()` allocates and initializes `struct configuration` and its `geometry`.
- `free_configuration()` frees geometry and configuration.
- `log_uds_configuration()` emits debug configuration fields.

## Dependencies
Uses buffer helpers, geometry construction, UDS parameters, logger, thread/core count helper, and project allocation wrappers.

## Important Behavior
Sparse indexing multiplies base chapters by 10 and marks 95% as sparse, increasing record capacity. Reduced memory modes subtract one chapter and are represented in version `08.02` via remapped chapter fields.

## Edge Cases
Invalid memory size returns `-EINVAL`. Configuration mismatch logs specific field differences and returns `UDS_NO_INDEX`.
