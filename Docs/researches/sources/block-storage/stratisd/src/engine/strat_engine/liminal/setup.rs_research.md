# File Research: sources/block-storage/stratisd/src/engine/strat_engine/liminal/setup.rs

## Purpose

`setup.rs` reconstructs pool setup inputs from liminal Stratis devices. It reads the newest available pool metadata, validates that discovered devices match that metadata, and converts device discovery records into ordered v1 or v2 `StratBlockDev` objects split by data and cache tier.

## Main Responsibilities

- Select the most recent pool metadata from BDAs by `last_update_time()`.
- Decode JSON metadata into `PoolSave`.
- Recover pool name and feature set only when discovered device UUIDs exactly match metadata UUIDs.
- Rebuild recorded allocation segment tables from `BackstoreSave`.
- Construct legacy v1 block devices, including encrypted underlying-device handles.
- Construct v2 block devices with integrity metadata allocations.
- Verify reconstructed devices against metadata, then sort them by recorded metadata order.

## Important Functions

- `get_metadata()` finds the BDA with the greatest update timestamp, opens its devnode, loads BDA state, and deserializes `PoolSave`.
- `get_name()` reads metadata, compares found UUIDs to recorded data/cache UUIDs, and returns `Name`.
- `get_feature_set()` performs the same UUID consistency check and returns `PoolFeatures`.
- `get_blockdevs_legacy()` builds v1 data/cache `StratBlockDev` vectors.
- `get_blockdevs()` builds v2 data/cache `StratBlockDev` vectors.
- `get_blockdev_legacy()` checks device size, locates tier metadata, sets up optional crypt handle, and calls `v1::StratBlockDev::new()`.
- `get_blockdev()` checks device size, locates tier metadata, asserts `info.luks == None`, carries integrity allocations, and calls `v2::StratBlockDev::new()`.
- `check_and_sort_devs()` rejects duplicate UUIDs, mixed metadata versions, and missing/extra devices, then sorts by metadata index.

## Behavior Details

The metadata read path is deliberately tolerant until it finds a candidate: devices without timestamps are ignored; the device with the newest timestamp is opened; failed open/load/deserialize attempts on that chosen device become a hard error because the timestamp says metadata should exist.

The block device setup path derives allocation segments from the metadata’s data-tier allocation list and, when present, cache-tier allocation lists. Those segments are keyed by parent device UUID and passed into each reconstructed block device.

Legacy setup handles encrypted devices by choosing the LUKS physical path when `info.luks` exists, attempting `CryptHandle::setup()`, and wrapping the result as `UnderlyingDevice::Encrypted` or `Unencrypted`. Current v2 setup expects the liminal device itself to be the usable devnode and asserts that no legacy `luks` info is attached.

## Dependencies and Interactions

- Consumes `LStratisInfo` from liminal device discovery.
- Uses BDA/MDA metadata loading through `info.bda`.
- Uses serde structures: `PoolSave`, `BackstoreSave`, `BaseBlockDevSave`, `PoolFeatures`.
- Constructs block devices from `backstore::blockdev::v1` and `v2`.
- Uses `blkdev_size()` to detect shrinkage before setup.
- Uses `CryptHandle` and `TokenUnlockMethod::None` for legacy encrypted setup.

## Notable Edge Cases

- A pool with timestamps but unreadable metadata returns an error rather than `None`.
- Found UUIDs must exactly equal metadata UUIDs for name and feature-set recovery.
- A device whose actual size is smaller than its recorded BDA size is rejected.
- Duplicate device UUIDs and mixed metadata versions are treated as setup errors.
- Missing or extra data/cache devices cause tier-specific consistency errors.
- `segments.unwrap_or(&vec![])` relies on temporary empty vectors only for the immediate constructor call.
