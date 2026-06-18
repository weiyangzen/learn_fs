# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/arc.c lines 1-8413

## Scope

This chunk covers the illumos ZFS ARC implementation from the file header through the beginning of L2ARC write-side data transforms. It includes the ARC theory comments, locking model, core tunables and kstats, DVA/birth keyed hash table, L1 ARC header/buffer lifecycle, compressed and encrypted buffer handling, ARC state transitions, eviction/reclaim, read/write entry points, dirty-data throttling, ARC initialization/finalization, and early L2ARC read/write/eviction support.

The chunk ends inside `l2arc_apply_transforms()` after allocating a compressed-data ABD and borrowing a temporary buffer. The rest of L2ARC write transforms, feed/write loops, device management, rebuild logic, and module teardown/tunable registration are outside this chunk.

## APIs And Entry Points

- Public ARC inspection/transform APIs: `arc_buf_size()`, `arc_buf_lsize()`, `arc_is_encrypted()`, `arc_is_unauthenticated()`, `arc_get_raw_params()`, `arc_get_compression()`, `arc_is_metadata()`, `arc_buf_thaw()`, `arc_buf_freeze()`, and `arc_untransform()`.
- Public buffer allocation and loan APIs: `arc_alloc_buf()`, `arc_alloc_compressed_buf()`, `arc_alloc_raw_buf()`, `arc_buf_alloc_l2only()`, `arc_loan_buf()`, `arc_loan_compressed_buf()`, `arc_loan_raw_buf()`, `arc_return_buf()`, and `arc_loan_inuse_buf()`.
- Public lifetime/mutation APIs: `arc_buf_destroy()`, `arc_freed()`, `arc_release()`, `arc_released()`, and debug-only `arc_referenced()`.
- Public I/O APIs: `arc_read()`, `arc_bcopy_func()`, `arc_getbuf_func()`, and `arc_write()`.
- Public memory/cache APIs: `arc_flush()`, `arc_memory_is_low()`, `arc_tempreserve_space()`, `arc_tempreserve_clear()`, `arc_max_bytes()`, `arc_init()`, and `arc_fini()`.

## State And Control Flow

- ARC identity is `(spa load guid, BP identity DVA, physical birth)`, stored in `buf_hash_table` with striped mutexes and CityHash indexing.
- Six ARC states are initialized: `arc_anon`, `arc_mru`, `arc_mru_ghost`, `arc_mfu`, `arc_mfu_ghost`, and `arc_l2c_only`, each with metadata/data multilists and size/evictable refcounts.
- `arc_buf_hdr_t` is the authoritative cache header; `arc_buf_t` is the consumer-visible buffer. Multiple buffers can share a header, and some may share the header’s linear ABD data when flags and ordering invariants allow it.
- `arc_buf_fill()` handles authentication, decryption, dnode in-place decryption, decompression, copying, byteswapping, and debug checksums.
- `arc_change_state()`, `add_reference()`, and `remove_reference()` coordinate state transitions, hash/list membership, L2ARC stats, and active versus evictable accounting.
- `arc_evict_hdr()`, `arc_evict_state()`, and `arc_adjust()` implement MRU/MFU eviction, ghost transitions, L2-only compaction, metadata/data balancing, and overflow waiter wakeups.
- `arc_read()` handles L1 hits, in-flight read joins, ghost/L2-only rehydration, optional L2ARC reads, and fallback `zio_read()`. `arc_read_done()` completes callbacks, handles transform errors, clears I/O state, and wakes waiters.
- `arc_write()` prepares raw/compressed/encrypted ZIO properties, detaches stale header data, and issues `zio_write()`. `arc_write_ready()` repopulates header data; `arc_write_done()` assigns final DVA/birth identity and inserts successful writes.
- `arc_release()` anonymizes a buffer before modification, either reusing a single-buffer header or splitting it into a new anonymous header.
- L2ARC logic covered here includes eligibility, write size/interval calculation, device rotation, write completion, read validation/fallback, sublist priority, log-block overhead, device-region eviction, and the start of write transforms.

## Dependencies

- ZFS SPA/vdev/ZIO, blkptr/DVA macros, checksum/compression, ABD, DMU byteswap/object types, DSL dirty-data accounting, ZIL MAC decoding, and ZFS ereports.
- Crypto helpers including `spa_do_crypt_abd()`, `spa_do_crypt_mac_abd()`, `spa_do_crypt_objset_mac_abd()`, `zio_crypt_decode_*()`, and later `dsl_crypto_key_t` use.
- illumos VM and kernel state: `physmem`, `freemem`, `needfree`, `lotsfree`, `desfree`, `availrmem`, `swapfs_minfree`, `pages_pp_maximum`, `heap_arena`, `zio_arena`, DNLC, kmem/vmem reaping, zthreads, kstats, multilists, refcounts, atomics, and DTrace.
- L2ARC device/log-block structures, vdev space accounting, SCL_L2ARC config locks, and persistence helpers declared here but mostly implemented later.

## Risks And Cross-Chunk References

- Header flags require the hash lock or an undiscoverable header; violating this can race lookup, eviction, read completion, or L2ARC updates.
- L2ARC paths intentionally use `mutex_tryenter()` to avoid hash-lock/`l2ad_mtx` deadlocks.
- Shared buffer accounting is fragile across `arc_share_buf()`, `arc_unshare_buf()`, `arc_buf_destroy_impl()`, `arc_release()`, and `arc_write()`.
- Eviction is best-effort and may not reclaim enough due to references, I/O, lock misses, prefetch lifetimes, or L2ARC writes.
- L2ARC hits are trusted only after checksum validation against the original BP; failures must fall back to primary storage.
- The chunk ends mid-`l2arc_apply_transforms()`. Chunk 2 must verify recompression/encryption behavior, cleanup paths, `abd_out` ownership, L2ARC feed/write loops, persistence rebuild helpers, device lifecycle, and final module plumbing.