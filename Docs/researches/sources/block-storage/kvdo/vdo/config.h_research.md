# File Research: sources/block-storage/kvdo/vdo/config.h

## Purpose
Defines UDS index configuration structures and public configuration lifecycle/serialization APIs.

## Key Constants
- `DEFAULT_VOLUME_INDEX_MEAN_DELTA = 4096`
- `DEFAULT_CACHE_CHAPTERS = 7`
- `DEFAULT_SPARSE_SAMPLE_RATE = 32`
- `MAX_ZONES = 16`

## Key Structures
- `struct configuration`: runtime configuration with device name, size, offset, geometry, nonce, zone/read thread counts, cache chapters, volume index delta, sparse sample rate.
- `struct uds_configuration_8_02`: persisted version including remapped virtual/physical chapter fields.
- `struct uds_configuration_6_02`: legacy persisted version without remapped fields.

## Public API
- `make_configuration()`
- `free_configuration()`
- `validate_config_contents()`
- `write_config_contents()`
- `log_uds_configuration()`

## Research Notes
This header bridges user-facing `uds_parameters`, runtime geometry, and stable on-disk index config.
