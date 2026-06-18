# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/config.h

## Purpose
`config.h` declares the UDS index configuration object and its versioned on-disk representations.

## Important APIs, Types, And Functions
- Defaults include `DEFAULT_VOLUME_INDEX_MEAN_DELTA`, `DEFAULT_CACHE_CHAPTERS`, `DEFAULT_SPARSE_SAMPLE_RATE`, and `MAX_ZONES`.
- `struct uds_configuration` holds the target block device, index size/offset, geometry, nonce, zone/read-thread counts, cache size, volume-index mean delta, and sparse sample rate.
- `struct uds_configuration_8_02` is the current persisted format with remapped virtual/physical chapter fields.
- `struct uds_configuration_6_02` is the older persisted format without remapping fields.
- Public APIs are `uds_make_configuration()`, `uds_free_configuration()`, `uds_validate_config_contents()`, `uds_write_config_contents()`, and `uds_log_configuration()`.

## Control Flow And Data Flow
The in-memory configuration combines user parameters and derived geometry. Save/load code uses the packed structures as size/layout references while actual encoding/decoding is performed through explicit little-endian helpers in `config.c`.

## State And Persistence Behavior
The packed structs are persistent metadata formats. The in-memory `uds_configuration` is used at runtime to size caches, choose concurrency, and verify that the index on disk belongs to the same nonce and geometry.

## Dependencies And Integration Points
The header includes `geometry.h`, `indexer.h`, and `io-factory.h`. It connects session parameters to index layout, volume index, and buffered metadata I/O.

## Risks
- On-disk structs are packed and version-sensitive; new fields require a new version strategy.
- `size_t`/`off_t` in runtime config are host-sized and must not be directly persisted.
- `MAX_ZONES` is used by other structures such as delta-index load arrays, so increasing it has wider memory/layout impact.

## Test Signals
Tests should verify structure sizes for packed versions, correct defaults in created configurations, and load/save compatibility with both 6.02 and 8.02 metadata.
