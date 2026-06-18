# File Research: sources/cow-pools/openzfs/module/zfs/uberblock.c

This file contains small helper routines for validating and updating ZFS uberblocks. It is part of subset A through `sources/cow-pools/openzfs`.

Primary APIs:
- `uberblock_verify(uberblock_t *ub)`
- `uberblock_update(uberblock_t *ub, vdev_t *rvd, uint64_t txg, uint64_t mmp_delay)`

Dependencies:
- `sys/uberblock_impl.h` defines `uberblock_t`, `UBERBLOCK_MAGIC`, and layout details.
- `sys/vdev_impl.h` supplies vdev and SPA state access.
- `sys/mmp.h` supplies multi-modifier protection fields/macros.
- `sys/zfs_context.h` supplies common kernel/platform helpers.

`uberblock_verify()` behavior:
- Detects byte-swapped uberblocks by comparing `ub_magic` to `BSWAP_64(UBERBLOCK_MAGIC)`.
- If byte-swapped, it byte-swaps the entire `uberblock_t` in place with `byteswap_uint64_array()`.
- Verifies that the resulting magic equals `UBERBLOCK_MAGIC`.
- Returns `0` on success or `SET_ERROR(EINVAL)` when the magic is invalid.

`uberblock_update()` behavior:
- Requires `ub->ub_txg < txg` via assertion.
- Updates the uberblock for a new transaction group.
- Writes `ub_magic`, `ub_txg`, root vdev GUID sum, timestamp, software version, MMP magic, MMP fields, and checkpoint txg.
- Deliberately does not set `ub_version`, preserving older uberblock version behavior for older pools.
- When multihost is enabled, stores the passed MMP delay and packs sequence, interval, and fail interval values into `ub_mmp_config`.
- When multihost is disabled, clears MMP delay and config.
- Always resets `ub_checkpoint_txg` to `0`.
- Returns true when the root block pointer’s logical birth matches the transaction group, indicating something changed in this txg.

Filesystem relevance:
- Uberblocks are the top-level persistent entry points for importing a ZFS pool. Their validity and endianness handling are critical for pool discovery.
- The update routine ties together transaction group advancement, GUID-sum consistency, software versioning, multihost protection, and checkpoint clearing.
- The function avoids changing the uberblock version, which preserves on-disk compatibility expectations.

Notable implementation details:
- Endianness conversion is in-place and only attempted when the magic matches the byte-swapped magic.
- MMP configuration is only meaningful for multihost pools and is cleared otherwise.
- The return value of `uberblock_update()` is not simply “updated”; it reports whether the root block pointer was born in the same transaction group.
