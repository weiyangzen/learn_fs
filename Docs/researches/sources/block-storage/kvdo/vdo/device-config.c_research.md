# File Research: sources/block-storage/kvdo/vdo/device-config.c

## Purpose
Parses and validates Device Mapper table arguments for the VDO target, owns `device_config` allocation/freeing, and validates whether a new table can modify an existing VDO.

## Main Behavior
- Supports table versions `V0` through `V4`, with argument-count compatibility arrays for older formats.
- Parses original table string for status/table output preservation.
- Extracts parent device name, physical block count, logical block size mode, cache size, block map age, optional settings, and thread counts.
- Handles legacy skipped fields: read cache options, MD RAID5 optimization, write policy, and pool name.
- Optional arguments include `deduplication`, `compression`, `maxDiscard`, and thread parameters (`cpu`, `ack`, `bio`, `bioRotationInterval`, `logical`, `physical`, `hash`).
- Opens the backing block device through `dm_get_device()` and fills version-0 physical size from the block device.

## Validation
- Logical size must be 4K-aligned.
- Logical, physical, and hash zone counts must be all zero or all non-zero.
- Block map cache must be sufficient for logical zones.
- Thread counts are bounded by constants and `cpu`/`bio` counts must be non-zero where required.
- `vdo_validate_new_device_config()` rejects changed target start, logical block size, shrinking logical size, cache size changes, block map age changes, physical shrink, and disallowed growth.

## Dependencies
Uses Linux DM APIs, VDO constants/types/status codes, UDS allocation/string helpers, logger, and VDO object references.

## Notable Risk
`vdo_validate_new_device_config()` compares `&config->thread_counts` to itself instead of comparing `to_validate->thread_counts` against `config->thread_counts`. As written, thread configuration changes are not detected by that check.
