# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdevmgr.rs

This file implements `BlockDevMgr<B>`, the generic manager for collections of backstore block devices. It owns the vector of blockdevs and a monotonic `TimeStamp` used for pool-level metadata writes. `TimeStamp::next()` returns current UTC time unless that would not advance beyond the last saved timestamp, in which case it adds one nanosecond.

The v1 specialization initializes devices through `initialize_devices_legacy()` with pool name, encryption info, and optional sector size. Adding v1 devices verifies pool UUID consistency, checks that existing encrypted pools can still be unlocked with their configured key/Clevis mechanisms, initializes new devices with default MDA size, and extends the device list. It also gathers pool encryption info across devices, reports encryption state, and delegates growth to the matching blockdev.

The v2 specialization initializes with `initialize_devices()` and has no per-device encryption parameters. Adding v2 devices only validates pool UUID and initializes new devices with default MDA size. Growth requires a `ValidatedIntegritySpec` and delegates to v2 blockdev growth.

The generic implementation provides UUID-to-device maps for rebuilding saved segment tables, destructive wipe of all blockdevs, immutable/mutable blockdev listing and lookup, removal of specified blockdevs followed by metadata wiping, atomic allocation, metadata replication, metadata loading, size/metadata/available accounting, and teardown. Allocation first checks aggregate free space, then walks blockdevs in order allocating partial ranges until each request is satisfied; because it checks total availability first, it asserts each request is fully allocated and returns all segment lists or `None`.

`save_state()` writes pool metadata to up to `MAX_NUM_TO_WRITE` randomly sampled candidate devices whose MDA can hold the metadata. It advances the timestamp only if at least one write succeeds. `load_state()` scans all devices and returns the newest metadata by update time, erroring if no metadata is available or any device reports a load error.

Tests cover allocation accounting, encrypted v1 add behavior with same/changed keyring keys, prevention of stealing blockdevs from another pool, and corresponding v2 ownership/accounting tests across loopback and real devices.
