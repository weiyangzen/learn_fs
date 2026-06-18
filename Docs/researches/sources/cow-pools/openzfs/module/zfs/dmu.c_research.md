# File Research: sources/cow-pools/openzfs/module/zfs/dmu.c

## Scope

Core Data Management Unit public data path. This file defines DMU object type metadata/byteswap tables, buffer hold APIs, bonus/spill handling, prefetch and eviction, long-range freeing, regular and UIO read/write paths, direct-I/O dispatch hooks, ARC buffer assignment, ZIL `dmu_sync()`, write policy selection, block cloning helpers, object info/byteswap functions, DMU subsystem init/fini, exported symbols, and module tunables.

## Main Interfaces

- Buffer holds: `dmu_buf_hold*()`, `dmu_buf_hold_array*()`, `dmu_buf_rele_array()`, `dmu_bonus_hold*()`, `dmu_spill_hold*()`.
- Bonus/spill metadata: `dmu_set_bonus()`, `dmu_set_bonustype()`, `dmu_get_bonustype()`, `dmu_rm_spill()`.
- Prefetch/evict: `dmu_prefetch()`, `dmu_prefetch_by_dnode()`, `dmu_prefetch_stream*()`, `dmu_prefetch_wait()`, `dmu_prefetch_dnode()`, `dmu_evict_range()`.
- Freeing: `dmu_free_long_range()`, `dmu_free_long_object()`, `dmu_free_range()`.
- Read/write: `dmu_read()`, `dmu_read_by_dnode()`, `dmu_write()`, `dmu_write_by_dnode()`, UIO variants under `_KERNEL`, `dmu_prealloc()`, `dmu_write_embedded()`, `dmu_redact()`.
- ARC/ZIL: `dmu_request_arcbuf()`, `dmu_return_arcbuf()`, `dmu_lightweight_write_by_dnode()`, `dmu_assign_arcbuf_by_dnode()`, `dmu_sync()`.
- Policy and metadata: `dmu_write_policy()`, `dmu_offset_next()`, `dmu_read_l0_bps()`, `dmu_brt_clone()`, `dmu_object_info*()`, byte-swap helpers.
- Lifecycle: `dmu_init()`, `dmu_fini()`.

## State And Control Flow

`dmu_ot[]` defines each DMU object type’s byteswap function, metadata/encryption flags, and description. `dmu_ot_byteswap[]` maps byteswap implementations to names.

The hold APIs convert object/offset ranges into dbufs. Single-buffer holds use `dbuf_hold()` and optional `dbuf_read()`. Array holds compute block count under `dn_struct_rwlock`, optionally create a root ZIO for parallel reads, prime zfetch, hold each dbuf, issue async reads, wait for ZIO completion and dbuf state transitions, and return an allocated dbuf pointer array. Write holds account RACCT write usage unless direct I/O is being used.

Prefetch supports bounded range prefetch at a requested level, stream priming through zfetch, synchronous wait-for-prefetch for full L0 ranges, and dnode-block prefetch. `dmu_prefetch_max` caps memory pressure for ordinary prefetch calls; `dmu_prefetch_wait()` intentionally reads the whole range in interruptible chunks.

Long-range freeing works backwards through the file, using `get_next_chunk()` to bound each transaction by L1 indirect coverage. It marks transactions net-free, throttles when per-txg dirty frees exceed `zfs_per_txg_dirty_frees_percent`, updates `dp_long_free_dirty_pertxg`, and frees ranges via `dnode_free_range()`. Full-object frees zero `dn_maxblkid` after success.

Regular reads can route aligned `DMU_DIRECTIO` requests to `dmu_read_abd()`; otherwise they hold readable dbufs in chunks and copy data to the caller buffer. Writes similarly use aligned `dmu_write_abd()` when possible or dirty/fill dbufs and copy caller data. UIO paths mirror this with `zfs_uio_fault_move()`, partial direct-I/O handling, and fallback to ARC-backed writes for unaligned tails.

`dmu_sync()` supports ZIL immediate block sync. It validates txg state, handles late-arrival writes for already-syncing txgs, chooses write policy, disables nopwrite when a current BP can change before the target txg, marks dirty records as `DR_IN_DMU_SYNC`, issues `arc_write()`, and publishes override BPs in `dmu_sync_done()`. Late arrivals allocate a new transaction, write a separate log block, add its txg to the lwb, and free the just-written block after log use.

`dmu_write_policy()` selects compression, checksum, dedup, verification, nopwrite, encryption, copies, gang copies, storage type, and small-block class behavior. It treats metadata, nofill/preallocated writes, regular data, encrypted objsets, DDT ZAP/log objects, redundant metadata settings, dedup checksums, and `WP_DMU_SYNC` differently.

Block cloning support reads L0 block pointers with `dmu_read_l0_bps()`, rejecting metadata, unsynced births, dirty non-BRT writes, and returning holes as zero BPs. `dmu_brt_clone()` dirties target dbufs as clone writes, verifies size compatibility, sets override BPs and logical births, marks BRT writes, and registers pending BRT references for non-hole, non-embedded blocks.

## Dependencies

Depends on dbuf/dnode/objset/DSL pool and dataset code, zfetch, ZIO/ARC/ABD, ZIL, BRT, SA cache, l2arc/arc lifecycle, ZAP, checksum/compression tables, ZFS UIO and RACCT helpers, range locking expectations for hole reporting, and module export/parameter infrastructure.

## Correctness Notes

Most operations carefully pair dnode struct locks with dbuf holds so dnode movement/eviction observes consistent holds. Array reads separate ZIO completion from dbuf state completion. `dmu_offset_next()` may force TXG sync for accurate hole reporting, but returns `EBUSY` rather than reporting unsafe holes. Nopwrite is disabled whenever the source BP could be invalidated by an earlier dirty record or free. Direct-I/O paths are delegated to `dmu_direct.c`, but regular paths clear `DMU_DIRECTIO` on misalignment. `dmu_sync()` return codes have caller-visible ZIL semantics: `EEXIST`, `ENOENT`, `EALREADY`, `EIO`, or initiated success.
