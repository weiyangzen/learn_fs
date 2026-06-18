# File Research: sources/block-storage/kvdo/vdo/device-config.h

## Purpose
Defines the parsed Device Mapper table configuration for a VDO target and declares config parsing/validation helpers.

## Main Structures
- `struct thread_count_config`: packed counts for bio ack, bio submit, rotation interval, CPU, logical, physical, and hash zones. The comment notes it is intended for equality comparison.
- `struct device_config`: owns DM target/device references, linked-list membership, original table string, parent device name, physical/logical sizing, block size/cache/age settings, dedupe/compression booleans, thread counts, and discard limit.

## API
- `vdo_as_device_config()` converts a list node to containing config.
- `vdo_parse_device_config()` builds a config from table args.
- `vdo_free_device_config()` releases DM device/string/config allocations.
- `vdo_set_device_config()` links/unlinks a config to a VDO.
- `vdo_validate_new_device_config()` checks table reload compatibility.

## Integration
This header is consumed by the DM target and by VDO lifecycle code that keeps all active table configs on `vdo->device_config_list`.
