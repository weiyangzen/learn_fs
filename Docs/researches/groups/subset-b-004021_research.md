# subset-b-004021 research

This grouped report covers Device Mapper bufio, cache metadata, cache policy registration, the SMQ policy, and associated cache support headers under `sources/distributed-fs/ceph-client/drivers/md`. Each section preserves the original source path so reconciliation can split it into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bufio.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-bufio.c

## Purpose
`dm-bufio.c` implements Device Mapper's buffered block I/O cache library. It gives metadata-heavy DM targets a block-oriented cache on top of a `block_device`, with read, get-if-present, new-buffer, prefetch, dirty tracking, writeback, discard/flush helpers, shrinker integration, and global cache-size enforcement.

## Important APIs, Types, and Functions
The central types are private `struct dm_bufio_client`, private `struct dm_buffer`, `struct dm_buffer_cache`, per-bucket `struct buffer_tree`, and an internal clock-style `struct lru`. Exported API includes `dm_bufio_client_create()`, `dm_bufio_client_destroy()`, `dm_bufio_client_reset()`, `dm_bufio_read()`, `dm_bufio_read_with_ioprio()`, `dm_bufio_get()`, `dm_bufio_new()`, `dm_bufio_prefetch()`, `dm_bufio_prefetch_with_ioprio()`, `dm_bufio_release()`, `dm_bufio_mark_buffer_dirty()`, `dm_bufio_mark_partial_buffer_dirty()`, `dm_bufio_write_dirty_buffers_async()`, `dm_bufio_write_dirty_buffers()`, `dm_bufio_issue_flush()`, `dm_bufio_issue_discard()`, `dm_bufio_forget()`, `dm_bufio_forget_buffers()`, `dm_bufio_set_minimum_buffers()`, `dm_bufio_get_device_size()`, and accessors for block number, data, aux data, client, block size, and dm-io client.

## Control Flow
Clients are created with a target block device, block size, reserve count, optional auxiliary per-buffer data, and optional callbacks. `new_read()` is the main read/new/get path: it first checks the rb-tree bucket without taking the client mutex, allocates or evicts a buffer if needed, inserts it with `B_READING` set for disk reads, submits I/O through `submit_io()`, waits unless doing `dm_bufio_get()`, and returns the data pointer plus a held `struct dm_buffer`. Dirty writes go through `dm_bufio_mark_partial_buffer_dirty()`, which moves buffers to the dirty LRU and records the dirty byte range. Writeback batches dirty buffers into a local list, submits writes under a plug, waits for `B_WRITING` to clear, moves clean buffers back to the clean LRU, and finally issues a flush for synchronous writeback.

## State and Persistence
Runtime state is in the client cache: rb-trees indexed by block, clean and dirty clock LRUs, hold counts, last access time, dirty/write byte ranges, and state bits `B_READING`, `B_WRITING`, and `B_DIRTY`. Persistent effects are only the block-device writes, flushes, and discards emitted by clients; the cache contents themselves are volatile. Module parameters control global cache size and retained bytes, while read-only counters expose current, peak, and allocator-class memory usage.

## Dependencies and Integration Points
The file depends on `linux/dm-bufio.h`, Device Mapper core logging, `dm-io`, block bio submission, workqueues, shrinkers, rbtrees, stack tracing in debug builds, and jump labels for no-sleep clients. DM metadata users such as persistent-data and cache metadata use bufio as their block cache. I/O uses direct bios when the buffer is not vmalloc-backed and small enough; otherwise it falls back to `dm_io()`.

## Risks and Edge Cases
Correctness depends on hold-count discipline: callers must release every buffer and must not dirty buffers still being read. `dm_bufio_get()` and prefetch intentionally avoid waiting for in-flight reads because they may be called from request context and waiting could deadlock. No-sleep clients switch from semaphores/mutexes to spinlocks and cannot evict buffers that require I/O waits. Shrinker and global cleanup race with normal use, so eviction predicates must reject held, dirty, writing, or reading buffers appropriately. Partial write ranges are aligned to at least 4 KiB and the physical block size, so wrong dirty ranges can write more data than the caller expects.

## Test Signals
Useful signals include repeated read/new/release cycles without leaked buffers, dirty partial writes followed by flush with correct on-disk data, prefetch not blocking request-context paths, shrinker-triggered eviction under memory pressure, no-sleep client behavior, discard and flush error propagation, module unload leak warnings staying quiet, and kmem/vmalloc allocation counters returning to zero after all clients are destroyed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-bufio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-builtin.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-builtin.c

## Purpose
`dm-builtin.c` contains `dm_kobject_release()`, a tiny release helper compiled into the kernel rather than into the unloadable DM module. Its purpose is to avoid executing a kobject release callback from module text after the DM module has been unloaded.

## Important APIs, Types, and Functions
The only exported function is `dm_kobject_release(struct kobject *kobj)`. It calls `complete(dm_get_completion_from_kobject(kobj))` and is exported with `EXPORT_SYMBOL`.

## Control Flow
When the last external reference to a DM kobject is dropped, the kobject core invokes this release method. The helper retrieves the completion embedded or associated by DM core and completes it, allowing `dm_sysfs_exit()` or related teardown code to finish waiting for final kobject release.

## State and Persistence
The file holds no state. It participates in teardown synchronization by completing a wait object owned by DM core. There is no persistent storage behavior.

## Dependencies and Integration Points
It includes `dm-core.h` for the completion lookup helper and integrates with DM sysfs/kobject lifetime management. The key integration constraint is link placement: this helper must stay built-in so it remains executable even if the DM module is unloaded.

## Risks and Edge Cases
Moving this function into unloadable module text reintroduces the documented race where another task drops the final kobject reference, completes teardown, gets preempted before returning, and later resumes in unloaded code. The helper also assumes the incoming kobject is one of the DM kobjects understood by `dm_get_completion_from_kobject()`.

## Test Signals
Relevant signals are clean DM device removal under concurrent sysfs/kobject reference churn, successful module unload after device teardown, and absence of use-after-free or execution-from-unloaded-module reports in KASAN/KCSAN or stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-builtin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-background-tracker.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-cache-background-tracker.c

## Purpose
`dm-cache-background-tracker.c` tracks pending cache policy background work for the DM cache target. It de-duplicates work by origin block, caps the amount of outstanding work, separates queued and issued work, and maintains counters for promotions, writebacks, and demotions.

## Important APIs, Types, and Functions
The private `struct background_tracker` stores `max_work`, atomic pending counters, `issued` and `queued` lists, and an rb-tree keyed by `policy_work.oblock`. Public functions are `btracker_create()`, `btracker_destroy()`, `btracker_queue()`, `btracker_issue()`, `btracker_complete()`, `btracker_nr_demotions_queued()`, and `btracker_promotion_already_present()`. The exported global `btracker_work_cache` supplies `struct bt_work` allocations.

## Control Flow
`btracker_queue()` allocates a `bt_work`, copies the policy work, inserts it in the rb-tree if no work for that origin block is already pending, and then places it either on `issued` when the caller wants the work pointer immediately or on `queued` for later issue. `btracker_issue()` moves the first queued item to `issued`. `btracker_complete()` uses `container_of()` on the policy work pointer, decrements counters, erases the rb-tree node, unlinks the list entry, and frees the object.

## State and Persistence
All state is volatile and expected to be protected by the caller, normally the policy spinlock. The rb-tree represents every pending queued or issued work item so duplicate origin-block migrations are rejected until completion. Atomic counters allow quick policy decisions such as counting queued demotions for free-space targets.

## Dependencies and Integration Points
The tracker depends on `dm-cache-policy.h` for `struct policy_work` and operation values, Linux lists/rbtrees/atomics/slab caches, and DM logging. The SMQ policy owns a tracker and calls it while deciding promotions, demotions, and writebacks. The cache target later performs the returned `policy_work` and calls back into policy completion, which completes the tracker entry.

## Risks and Edge Cases
The header explicitly says there is no internal locking; callers must serialize every operation. `btracker_destroy()` asserts that no issued work remains, so policy teardown must first drain or complete issued operations. Duplicate work returns `-EINVAL` after freeing the second allocation, which policy callers treat as a benign race. Reaching `max_work` returns `-ENOMEM`, so callers must restore entry queue state when queueing fails.

## Test Signals
Tests should cover duplicate oblock queue rejection, queue-to-issued transitions, immediate issue through the `pwork` argument, correct pending counters by work type, max-work backpressure, destroy with queued but unissued work, and destroy assertions catching leaked issued work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-background-tracker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-background-tracker.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-cache-background-tracker.h

## Purpose
`dm-cache-background-tracker.h` declares the background-work tracker interface used between DM cache policies and the cache target. It documents that the tracker is an unlocked mediator for policy-selected promotions, demotions, and writebacks.

## Important APIs, Types, and Functions
The header defines `struct bt_work`, with list linkage, rb-tree node, and embedded `struct policy_work`. It forward-declares `struct background_tracker`, exports `btracker_work_cache`, and declares create, destroy, queue, issue, complete, demotion-count, and promotion-presence functions.

## Control Flow
The header itself has no execution path, but its contract is that policies queue copied work, the target issues queued work through the same internal pointer, and completion gives that pointer back so the tracker can remove exactly the tracked object.

## State and Persistence
No persistent state is declared. The documented state model is in-memory only, with queued, issued, and pending-by-oblock membership maintained by the implementation.

## Dependencies and Integration Points
It includes `dm-cache-policy.h` for policy work definitions and Linux vmalloc/list/rbtree visibility through included kernel headers. It is consumed by `dm-cache-policy-smq.c` and implemented by `dm-cache-background-tracker.c`.

## Risks and Edge Cases
The no-locking warning is the main risk: using the API without a surrounding spinlock or equivalent can corrupt lists/rbtrees or double-complete work. Callers must pass the same `policy_work *` received from queue/issue into completion, because the pointer identifies the containing `bt_work`.

## Test Signals
Compile coverage should verify all policy users agree on `struct bt_work` layout. Runtime tests are the implementation tests: no duplicate promotions, no leaked issued work, and stable behavior under concurrent policy decisions protected by the policy lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-background-tracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-block-types.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-cache-block-types.h

## Purpose
`dm-cache-block-types.h` creates sparse-distinct integer types for cache metadata block domains: origin blocks, cache blocks, and discard-bitset blocks. This prevents accidental mixing of indexes that have different meanings.

## Important APIs, Types, and Functions
The header typedefs `dm_oblock_t`, `dm_cblock_t`, and `dm_dblock_t` as `__bitwise` wrappers over `dm_block_t` or `uint32_t`. Conversion helpers are `to_oblock()`, `from_oblock()`, `to_cblock()`, `from_cblock()`, `to_dblock()`, and `from_dblock()`.

## Control Flow
There is no runtime control flow beyond inline casts. Callers explicitly convert at API boundaries, arithmetic sites, and persistent encoding/decoding points.

## State and Persistence
No state is stored here. The type choices affect persistence because metadata packing stores origin blocks, cache blocks, and discard blocks using the correct converted integer widths.

## Dependencies and Integration Points
It includes the persistent-data block manager for `dm_block_t`. It is included by cache metadata and policy headers, making the typed block aliases part of the cache target's internal ABI.

## Risks and Edge Cases
`dm_cblock_t` is backed by `uint32_t`, so cache block counts and indexes must fit that width. The `__force` conversions are intentionally explicit; overusing them can bypass sparse's protection and hide domain errors.

## Test Signals
Sparse builds should catch accidental assignment between block domains. Functional signals include correct mapping load/insert/remove behavior when origin, cache, and discard indexes differ substantially.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-block-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-metadata.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-cache-metadata.c

## Purpose
`dm-cache-metadata.c` manages the persistent metadata format for the DM cache target. It formats or opens the metadata device, validates and commits the superblock, stores cache-block to origin-block mappings, dirty bits, discard bits, policy hints, feature flags, and statistics, and provides transaction/abort/read-only control around persistent-data objects.

## Important APIs, Types, and Functions
Key structures are on-disk `struct cache_disk_superblock` and in-memory `struct dm_cache_metadata`. Public APIs include `dm_cache_metadata_open()`, `dm_cache_metadata_close()`, `dm_cache_resize()`, `dm_cache_discard_bitset_resize()`, `dm_cache_load_discards()`, `dm_cache_set_discard()`, `dm_cache_insert_mapping()`, `dm_cache_remove_mapping()`, `dm_cache_load_mappings()`, `dm_cache_set_dirty_bits()`, `dm_cache_metadata_get_stats()`, `dm_cache_metadata_set_stats()`, `dm_cache_commit()`, `dm_cache_get_free_metadata_block_count()`, `dm_cache_get_metadata_dev_size()`, `dm_cache_write_hints()`, `dm_cache_metadata_set_read_only()`, `dm_cache_metadata_set_read_write()`, `dm_cache_metadata_set_needs_check()`, `dm_cache_metadata_needs_check()`, `dm_cache_metadata_abort()`, and `dm_cache_metadata_clean_when_opened()`.

## Control Flow
Open goes through a refcounted global table keyed by metadata bdev, creates a block manager, detects all-zero unformatted superblocks, formats if allowed, or validates and opens existing metadata. Formatting creates a transaction manager, mapping array, optional separate dirty bitset for metadata version 2, discard bitset, and initial superblock. Normal mutation takes `root_lock`, updates dm-array or dm-bitset roots, marks `changed`, and leaves persistence to `dm_cache_commit()`. Commit flushes dirty/discard roots, pre-commits the transaction manager, copies the space-map root, writes the superblock fields and clean-shutdown flag, commits, then begins a new transaction by rereading the superblock.

## State and Persistence
Persistent state lives in a checksummed superblock at block 0 plus persistent-data roots for mapping, hints, discard bits, and, for version 2, a separate dirty bitset. Version 1 stores dirty state in low mapping flags; version 2 separates dirty bits. `CLEAN_SHUTDOWN` controls whether loaded mappings and discards are trusted as clean or conservatively treated dirty/undiscarded after a crash. `NEEDS_CHECK` persists a tools-required repair flag. Runtime state includes open refcount, policy identity, stats, roots, block counts, cursors, and `fail_io`, which restricts operations after an abort rollback failure.

## Dependencies and Integration Points
The file integrates with persistent-data components: block manager, transaction manager, metadata space map, dm-array, and dm-bitset. It depends on cache policy identity and hint APIs from `dm-cache-policy-internal.h`, typed block wrappers, and block-device read-only state. The DM cache target uses it to load mappings into the selected policy, persist dirty bits and hints during suspend/commit, and recover metadata after crashes.

## Risks and Edge Cases
Changing the data block size on reopen is rejected. Unsupported incompat or read-write incompatible feature flags prevent opening. Cache shrink first verifies removed blocks are unmapped or clean; dirty blocks make shrink fail. If the previous shutdown was unclean, mappings load as dirty and discard bits load as false to avoid data loss. `dm_cache_metadata_abort()` intentionally creates a new block manager outside `root_lock` to avoid an ABBA deadlock with shrinker teardown; failure sets `fail_io`, after which only close is safe. Policy hints are trusted only when the policy name, major version, hint size, and clean-open state match.

## Test Signals
Important signals include format and reopen across metadata versions 1 and 2, checksum/magic/version rejection, clean versus unclean shutdown mapping load semantics, shrink rejection with dirty blocks, discard bitset resize/load behavior, policy hint preservation and invalidation after policy changes, needs-check persistence, read-only mode rejecting writes, abort success and fail-io behavior, and transaction commits preserving stats and roots across reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-metadata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-metadata.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-cache-metadata.h

## Purpose
`dm-cache-metadata.h` exposes the persistent metadata API used by the DM cache target and policies. It defines metadata device sizing limits, feature flag masks, the opaque metadata handle, statistics, and all mapping, discard, dirty, hint, commit, and recovery operations.

## Important APIs, Types, and Functions
The header defines `DM_CACHE_METADATA_BLOCK_SIZE`, maximum metadata-device sector constants, supported feature masks, opaque `struct dm_cache_metadata`, callback types `load_discard_fn` and `load_mapping_fn`, `struct dm_cache_statistics`, and declarations for open/close, cache resize, discard bitset resize/load/set, mapping insert/remove/load, dirty bit import, stats get/set, commit, metadata-space queries, hint writing, needs-check/read-only/read-write/abort controls, and clean-open query.

## Control Flow
The intended flow is: open or format metadata, resize structures to match cache/discard geometry, load discards and mappings into runtime target and policy state, perform mapping/dirty/discard mutations while I/O runs, write policy hints and stats, and call `dm_cache_commit()` at transaction boundaries or clean shutdown. Recovery paths may set needs-check, switch read-only/read-write, or abort back to the last good transaction.

## State and Persistence
The header describes persistent metadata but stores no state itself. API comments clarify that policy hints are persistent only across clean operation with matching policy identity, and may be lost after crashes or policy changes.

## Dependencies and Integration Points
It includes cache block types, policy internals, and persistent-data metadata space-map sizing. It is the contract between `dm-cache-target.c` and the metadata implementation, and it also depends on policy APIs for hint sizing and hint extraction.

## Risks and Edge Cases
The maximum metadata size constants impose a hard cap and warning threshold. Feature masks are all zero in this version, so any future on-disk feature flag must update the masks correctly. `dm_cache_set_dirty_bits()` requires the caller's bitset to match cache size for version 2 metadata.

## Test Signals
Compile tests should exercise all target call sites. Runtime signals come from the implementation: correct load callbacks, commit/reopen persistence, clean-open reporting, needs-check behavior, and safe handling of read-only or abort states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy-internal.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy-internal.h

## Purpose
`dm-cache-policy-internal.h` provides inline wrappers and helper allocation utilities for DM cache policy users and policy implementations. It normalizes optional policy callbacks and exposes policy creation/destruction and identity accessors used by the cache target and metadata code.

## Important APIs, Types, and Functions
Wrappers include `policy_lookup()`, `policy_lookup_with_work()`, `policy_get_background_work()`, `policy_complete_background_work()`, `policy_set_dirty()`, `policy_clear_dirty()`, `policy_load_mapping()`, `policy_invalidate_mapping()`, `policy_get_hint()`, `policy_residency()`, `policy_tick()`, `policy_emit_config_values()`, `policy_set_config_value()`, and `policy_allow_migrations()`. Utility helpers include `bitset_size_in_bytes()`, `alloc_bitset()`, `clear_bitset()`, and `free_bitset()`. External declarations expose `dm_cache_policy_create()`, `dm_cache_policy_destroy()`, name/version getters, and hint-size getter.

## Control Flow
The wrappers mostly dispatch directly through function pointers in `struct dm_cache_policy`. Optional hooks have defaults: `lookup_with_work` falls back to `lookup`, `get_hint` returns zero when absent, `tick` is skipped when absent, config emission reports zero values when absent, and unsupported config set returns `-EINVAL`.

## State and Persistence
No persistent state is owned by the header. The bitset helpers allocate volatile vmalloc-backed bitsets used by policies such as SMQ for per-period hit tracking. Identity getters are used by metadata to decide whether persisted policy hints are compatible.

## Dependencies and Integration Points
It includes `dm-cache-policy.h` and Linux vmalloc support. The DM cache target uses these wrappers instead of reaching into policy function pointers directly, while policy implementations use the bitset helpers.

## Risks and Edge Cases
The fallback in `policy_lookup_with_work()` passes `NULL` for `background_queued`; policy implementations must tolerate that if they are used through the fallback. `policy_allow_migrations()` is not optional here, so every registered policy must provide it. `DMEMIT` in config emission assumes the caller has provided the usual `result`, `maxlen`, and size pointer context.

## Test Signals
Tests should exercise policies with and without optional callbacks, config status output for policies with no config, hint defaulting to zero, and bitset allocation/clear/free for cache sizes crossing word boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy-smq.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy-smq.c

## Purpose
`dm-cache-policy-smq.c` implements the stochastic multi-queue cache replacement policy for DM cache. It decides cache hits, promotions, demotions, and writebacks using multi-level queues for cache and hotspot entries, periodic hit sampling, sentinels for age thresholds, and a background-work tracker.

## Important APIs, Types, and Functions
Core data structures are `struct entry`, `struct entry_space`, `struct ilist`, `struct queue`, `struct stats`, `struct smq_hash_table`, `struct entry_alloc`, and `struct smq_policy`. The policy vtable functions are `smq_lookup()`, `smq_lookup_with_work()`, `smq_get_background_work()`, `smq_complete_background_work()`, `smq_set_dirty()`, `smq_clear_dirty()`, `smq_load_mapping()`, `smq_invalidate_mapping()`, `smq_get_hint()`, `smq_residency()`, `smq_tick()`, `smq_allow_migrations()`, and destroy/config helpers. Module init registers policy types `smq`, `mq`, `cleaner`, and alias `default`.

## Control Flow
Lookup first checks the cache hash table. Hits update cache statistics, requeue the entry upward once per tick period, and return the inferred cblock. Misses update the hotspot queue keyed by a larger hotspot block, assess whether the hotspot level crosses read/write promotion thresholds, and possibly queue promotion work. Background work retrieval first issues already queued work; if idle or cleaner mode needs more clean blocks, it queues writeback before issuing. Completion clears pending state and either installs promoted mappings, frees demoted entries, or requeues writeback entries.

## State and Persistence
SMQ state is volatile policy state protected by `mq->lock`: cache entries, hotspot entries, clean/dirty queues, hash tables, hit bitsets, queue statistics, sentinel generation flags, migration flags, and the background tracker. Persistence is indirect: `smq_load_mapping()` restores mappings and dirty state from metadata, and `smq_get_hint()` returns an entry level that metadata can persist as a 32-bit policy hint. Registered policy type versions and hint size form the compatibility identity for persisted hints.

## Dependencies and Integration Points
The policy uses the background tracker, cache policy internal wrappers, typed block APIs, Linux hashing/jiffies/vmalloc/math helpers, and DM policy registration. The cache target calls the policy vtable to map I/O, request background migrations, mark dirty/clean state after writes or writebacks, load mappings from metadata, and save hints on commit.

## Risks and Edge Cases
The implementation is lock-sensitive: nearly all policy mutation must happen under the spinlock, while `smq_load_mapping()` is intended for single-threaded load. The code has an explicit FIXME in `smq_invalidate_mapping()` for invalidating blocks with pending background work. Promotion allocates the destination cache entry before work starts; failed queueing or failed completion must free it or residency leaks. Cleaner policy disables migrations but tries to clean all dirty entries. The `mq` compatibility policy accepts old tunables but ignores them, so user space may believe knobs still matter unless it reads warnings/status.

## Test Signals
Test signals include cache hit/miss mapping decisions, promotion queueing only above thresholds or for fast writes, demotion when free targets are unmet, writeback when idle/cleaner requires cleaning, completion success and failure for all work types, loading mappings with valid and invalid hints, preserving policy hints across clean shutdown, rejecting duplicate background work, status output for `mq` compatibility tunables, and module registration/unregistration for all aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy-smq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy.c

## Purpose
`dm-cache-policy.c` implements the registry and factory for DM cache policy modules. It lets policy implementations register named types, supports module auto-loading by policy name, pins owner modules while policies are live, and exposes policy identity helpers.

## Important APIs, Types, and Functions
The private registry is `register_list` protected by `register_lock`. Public functions are `dm_cache_policy_register()`, `dm_cache_policy_unregister()`, `dm_cache_policy_create()`, `dm_cache_policy_destroy()`, `dm_cache_policy_get_name()`, `dm_cache_policy_get_version()`, and `dm_cache_policy_get_hint_size()`. Internal helpers include `__find_policy()`, `__get_policy_once()`, `get_policy_once()`, `get_policy()`, and `put_policy()`.

## Control Flow
Policy creation looks up a registered type under the spinlock and tries to get its module reference. If missing, it calls `request_module("dm-cache-%s", name)` and retries. It then invokes the type's `create()` method and stores the policy type in `p->private`. Destroy calls the policy's `destroy()` method and drops the module reference. Registration rejects duplicate names and hint sizes other than 0 or 4 bytes.

## State and Persistence
The registry state is in-memory only. The policy type pointer stored in each policy object is runtime state used for destroy and identity access. Persistent metadata uses the name, version, and hint size returned by this registry path to validate saved hints.

## Dependencies and Integration Points
The file depends on Linux module loading/refcounting, lists, spinlocks, slab error conventions, DM logging, and the policy structs from `dm-cache-policy-internal.h`. SMQ and other policy modules register through this API; the cache target creates selected policies through it.

## Risks and Edge Cases
Owner module pinning can fail, in which case lookup returns an error-like pointer internally and creation reports unknown policy. Alias policy types use `real` so `dm_cache_policy_get_name()` returns the real policy name for metadata compatibility, while version currently comes from the alias type. Unregister does not wait for live users itself; correctness depends on module references taken during create.

## Test Signals
Useful signals include duplicate registration rejection, invalid hint-size rejection, auto-loading by policy name, create/destroy balancing module refs, alias name reporting for `default`, and clean unregister after policy module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy.h

## Purpose
`dm-cache-policy.h` defines the public internal contract implemented by DM cache replacement policies and consumed by the cache target. It describes policy work operations, the policy vtable, and the policy type registration format.

## Important APIs, Types, and Functions
`enum policy_operation` defines `POLICY_PROMOTE`, `POLICY_DEMOTE`, and `POLICY_WRITEBACK`. `struct policy_work` carries an operation plus origin and cache block identifiers. `struct dm_cache_policy` is the vtable for lookup, optional immediate-work lookup, background work issue/complete, dirty state updates, metadata load/invalidate, hint access, residency, tick, config, and migration control. `struct dm_cache_policy_type` describes named policy plugins with version, alias target, hint size, owner module, and create callback. The exported registry declarations are `dm_cache_policy_register()` and `dm_cache_policy_unregister()`.

## Control Flow
Policies are instantiated by the registry, then the cache target repeatedly calls lookup on I/O, asks for background work, completes work, updates dirty state, and periodically calls tick. Metadata load calls `load_mapping()` before normal I/O. During shutdown or commit, the target can query hints and config/status.

## State and Persistence
The header owns no state. It defines how policies expose volatile decisions and how they provide persistent hint values. Policy name, major version, and hint size are persisted by metadata to decide whether saved hints are reusable.

## Dependencies and Integration Points
It includes cache block types and `linux/device-mapper.h` for DM status emission and kernel types. It is included by policy implementations, the policy registry, the background tracker, cache metadata, and the cache target.

## Risks and Edge Cases
The lookup contract says it must not block and may return `-EWOULDBLOCK`; policy implementations need to honor block-layer constraints. `complete_background_work()` requires the exact work pointer originally returned, not a copy, because implementations may embed it in tracked state. Hint size is currently constrained by the registry to 0 or 4 bytes.

## Test Signals
Compile and runtime tests should validate every policy implementation fills required callbacks, lookup does not sleep in request context, background work pointer identity is preserved, dirty state callbacks match metadata dirty bits, and policy status/config behavior remains stable for user space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy.h -->
