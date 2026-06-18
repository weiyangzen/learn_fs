# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/data_tier.rs

This file implements `DataTier<B>`, the base data layer under the cap device. It owns a `BlockDevMgr<B>`, the upper-layer data segments allocated from managed blockdevs, and an optional `ValidatedIntegritySpec`. The generic implementation handles setup, allocation, size accounting, persistence, destruction, use partitioning, invariants, and serialization; v1/v2 specializations handle version-specific construction, add, lookup, and growth.

For v1, `new()` creates an empty data tier with no integrity spec and no allocated upper segments. Adding devices delegates to the v1 block manager with pool name, pool UUID, devices, and optional sector size. Growth delegates directly to v1 manager growth.

For v2, `new()` requires an integrity spec and immediately reserves integrity metadata from the back of every managed blockdev using `integrity_meta_space(total_size, spec)`. Adding v2 devices initializes them, filters the newly added UUIDs, asserts all were found, and reserves integrity metadata for each new blockdev. Growth delegates to v2 manager growth with the stored integrity spec.

`setup()` reconstructs an existing data tier by mapping saved allocation records through a uuid-to-device-number map and preserving the saved integrity spec. `alloc()` asks the block manager for requested sector lengths and, if successful, coalesces all returned block-device segments into the tier's `AllocatedAbove` segment list. It returns a boolean rather than the segments, because the tier stores the canonical allocation map internally.

Accounting methods report allocated upper data, raw size, metadata size, and usable size. Metadata size comes from blockdev metadata accounting; for v2 this includes BDA plus per-device integrity reservations, while cap-level crypt metadata is accounted in v2 backstore rather than here. `save_state()` and `load_state()` delegate pool metadata replication to the block manager. `partition_by_use()` supports action availability checks by splitting blockdevs into used and unused sets.

Serialization writes one allocation vector for data segments, blockdev records, and the optional integrity spec. Tests for both versions allocate data, add devices, verify allocation is unchanged after add, force allocation onto new devices, check invariants, and destroy the tier.
