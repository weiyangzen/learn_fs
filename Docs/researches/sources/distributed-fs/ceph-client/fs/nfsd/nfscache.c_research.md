# sources/distributed-fs/ceph-client/fs/nfsd/nfscache.c

## Purpose

`sources/distributed-fs/ceph-client/fs/nfsd/nfscache.c` implements the NFSD duplicate reply cache (DRC). The cache detects retransmitted non-session NFS RPC calls, drops duplicate in-progress requests, and replays cached replies for completed requests when safe. It also sizes, initializes, prunes, shrinks, updates, and reports statistics for the per-network-namespace reply cache. The source was read as a complete 667-line file.

## Important APIs, Types, and Functions

Public entry points are `nfsd_drc_slab_create()`, `nfsd_drc_slab_free()`, `nfsd_reply_cache_init()`, `nfsd_reply_cache_shutdown()`, `nfsd_cache_lookup()`, `nfsd_cache_update()`, and `nfsd_reply_cache_stats_show()`. `struct nfsd_drc_bucket` contains the per-bucket rb-tree root, LRU list, and spinlock. Cache entries are `struct nfsd_cacherep` objects allocated from the global `drc_slab`; they carry request key fields, state (`RC_UNUSED`, `RC_INPROG`, `RC_DONE`), reply type (`RC_NOCACHE`, `RC_REPLSTAT`, `RC_REPLBUFF`), secure-request flag, timestamp, rb-node, LRU node, and cached reply payload/status.

Important helpers include `nfsd_cache_size_limit()` and `nfsd_hashsize()` for sizing, `nfsd_cacherep_alloc()`/`nfsd_cacherep_free()` for entry lifetime, `nfsd_cacherep_unlink_locked()` for unlinking and accounting, `nfsd_prune_bucket_locked()` and shrinker callbacks for reclamation, `nfsd_cache_csum()` for weak checksums over request headers, `nfsd_cache_key_cmp()` and `nfsd_cache_insert()` for rb-tree lookup/insert, and `nfsd_cache_append()` for replaying cached reply buffers into an XDR response stream.

## Control Flow

Initialization uses `nfsd_reply_cache_init()` per `struct nfsd_net`: compute a max entry limit from low memory, round bucket count up based on `TARGET_BUCKET_SIZE`, allocate the bucket table with `kvzalloc()`, allocate/register a shrinker, initialize bucket LRUs and locks, and store hash metadata. Shutdown unregisters/frees the shrinker, walks each bucket LRU, frees all cache entries under bucket locks, and releases the bucket table.

Lookup starts in `nfsd_cache_lookup()`. If the current procedure's thread-local cache type is `RC_NOCACHE`, the function records a no-cache stat and returns `RC_DOIT`. Otherwise it computes a checksum over the NFS call header, preallocates a candidate entry, selects a bucket by XID hash, and calls `nfsd_cache_insert()` under the bucket lock. A true miss installs the new entry as `RC_INPROG`, prunes a few old entries from the bucket LRU, drops the lock, disposes pruned entries, accounts a miss, and tells the caller to process normally with `*cacherep` set.

If lookup finds an existing entry, the preallocated candidate is freed, hit stats are incremented, and the default result is `RC_DROPIT`. `RC_INPROG` entries remain drops so another server thread does not process the same RPC concurrently. Completed entries are replayed only if the original secure transport requirements are met; insecure retransmits cannot use replies cached from secure requests. Depending on cached reply type, lookup either does nothing for `RC_NOCACHE`, encodes a cached status word for `RC_REPLSTAT`, or appends a cached reply buffer for `RC_REPLBUFF`, returning `RC_REPLY` when replay succeeds.

Update happens in `nfsd_cache_update()` after procedure execution. It finds the same bucket, computes the word length from the status pointer to the current response head end, rejects excessive replies and encode failures, stores either a single status or a kmalloc-copied reply buffer, then under lock updates memory accounting, moves the entry to the LRU tail, records whether the request was secure, sets the reply type, and marks the entry `RC_DONE`.

## State and Persistence Behavior

The DRC is in-memory, per NFSD network namespace, and not persistent across server restart or netns teardown. Bucket rb-trees provide exact request-key lookup; bucket LRU lists provide age-based pruning. The request key includes XID, procedure, client address and port, transport protocol, RPC version, argument length, and checksum of leading call bytes. The checksum is deliberately weak and used as a key discriminator, not as cryptographic authentication.

Memory accounting is maintained through `atomic_t num_drc_entries` and NFSD stats counters for DRC memory usage, hits, misses, no-cache calls, payload misses, and longest rb-chain observations. Entries expire by `RC_EXPIRE` and are also pruned when the cache exceeds `max_drc_entries` or when the shrinker asks for reclaim.

## Dependencies and Integration Points

The file depends on SUNRPC request/transport structures, XDR buffers and streams, network address helpers, kernel slab/vmalloc/shrinker APIs, rb-trees, list LRUs, spinlocks, checksum helpers, page access, NFSD per-net state in `netns.h`, cache type definitions in `cache.h`, and tracepoints. It integrates with NFSD dispatch through `nfsd_cache_lookup()` before executing a request and `nfsd_cache_update()` after encoding a reply. It also integrates with proc/seq reporting through `nfsd_reply_cache_stats_show()`.

The cache is especially relevant for NFS versions/procedures without NFSv4.1 session replay semantics. `nfs4xdr.c` disables this DRC path for minor versions with sessions, while NFSv2/v3 and NFSv4.0 cacheable operations use the same infrastructure through thread-local `ntli_cachetype`.

## Risks and Edge Cases

The lookup/update path is concurrency-sensitive. The preallocate-then-insert design avoids allocation under the bucket lock but requires freeing the unused candidate correctly on hits. `RC_INPROG` duplicate handling intentionally drops retransmits, so stale in-progress entries must eventually expire or be removed. Reply caching only copies up to 256 bytes from the status pointer region; larger or failed encodings are uncached and the in-progress entry is removed.

Security behavior depends on `c_secure`: replies generated for secure requests are not replayed to insecure retransmits. Request identity relies on address, port, XID, argument length, and checksum; checksum collisions are possible, but mismatching checksums for equal XID are traced and counted. The shrinker scans all buckets and removes only expired or over-limit entries, so memory pressure behavior depends on timestamps and LRU ordering. `nfsd_prune_bucket_locked()` uses a `max` limit but increments after unlinking, so callers should treat it as an approximate pruning bound.

## Test Signals

Useful tests include retransmission/replay tests for cacheable NFS procedures, duplicate in-progress request drops, secure-to-insecure replay denial, large reply no-cache behavior, encode-failure cleanup with `statp == NULL`, shrinker/prune behavior under low memory or forced cache limits, and netns init/shutdown leak checks. Runtime signals include DRC tracepoints for found/mismatch events and `/proc`/seq stats for hits, misses, no-cache calls, payload misses, memory usage, and longest chain length.
