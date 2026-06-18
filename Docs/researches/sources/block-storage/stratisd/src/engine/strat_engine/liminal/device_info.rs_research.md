# File Research: sources/block-storage/stratisd/src/engine/strat_engine/liminal/device_info.rs

This file defines the data structures for devices known to Stratis but not necessarily assembled into active pools.

Key types:
- `LLuksInfo`: discovered Stratis-owned LUKS device, including device node, identifiers, encryption info, and optional pool name.
- `LStratisInfo`: discovered Stratis metadata device, optionally linked to its backing LUKS info.
- `LInfo`: enum over closed LUKS-only info and opened Stratis-device info.
- `DeviceSet`: map of device UUID to merged device information for one pool.
- `DeviceBag`: miscellaneous set that can contain duplicate UUID concepts for looser tracking.

Key responsibilities:
- Merge LUKS and Stratis observations for the same pool/device UUID.
- Detect conflicts in device number or encryption metadata and retain older known-good info when newer info conflicts.
- Represent whether a pool has closed encrypted devices.
- Convert complete opened sets into blockdev info for setup.
- Gather pool encryption info, pool name, feature metadata, stopped-pool info, locked-pool info, and metadata version.
- Process udev add/remove state transitions, including reverting an opened encrypted device back to a closed LUKS entry when the mapped Stratis device disappears.
- Serialize liminal device state to JSON.

Important behavior:
- `DeviceSet::into_opened_set()` refuses closed encrypted devices.
- `locked_pool_info()` filters out incomplete encrypted observations where a Stratis device lacks its associated LUKS info.
- `stopped_pool_info()` reports either physical LUKS nodes or direct Stratis nodes, depending on encryption state.
- Mixed metadata versions in one set are treated as an error.

Tests:
- No local tests in this file.
