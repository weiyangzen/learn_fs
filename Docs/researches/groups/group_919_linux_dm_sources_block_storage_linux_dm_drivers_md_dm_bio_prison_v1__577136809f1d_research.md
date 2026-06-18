# Group Research: group_919_linux_dm_sources_block_storage_linux_dm_drivers_md_dm_bio_prison_v1__577136809f1d

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v1.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v1.c

Implements the original Device Mapper "bio prison": a spinlock-protected red-black tree of keyed cells used to detain bios that cannot be processed immediately. Keys compare by virtual/physical namespace, thin device id, and overlapping block ranges; overlapping keys resolve to the same cell, so only one holder proceeds while later bios are appended to that cell.

The prison owns a mempool backed by `dm_bio_prison_cell` slab objects with a minimum of 1024 cells. Public entry points allocate/free cells, create/destroy prisons, get or create cells, detain bios, release cells, release without holder, error all bios, visit-and-release under lock, and promote a waiting inmate to holder.

Release paths erase the cell from the rb-tree and optionally merge the holder and inmates into a caller-provided `bio_list`. Error release sets `bi_status` and completes each bio. Promotion avoids a race between empty-cell release and new inmates by deciding under the prison lock.

The second half implements `dm_deferred_set`, a 64-entry ring of deferred counters and work lists used to delay work until earlier shared reads complete. `dm_deferred_entry_inc()` pins the current entry; `dm_deferred_entry_dec()` decrements and sweeps ready work; `dm_deferred_set_add_work()` either queues work behind outstanding entries or returns that no deferral is needed. Module init/exit initializes both v1 and v2 bio-prison slab caches.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v1.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v1.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v1.h

Declares the v1 bio-prison API and exposes `struct dm_bio_prison_cell` layout so callers can preallocate and manage cell memory. A cell contains a client `user_list`, rb-tree node, range key, current holder bio, and detained bio list.

`struct dm_cell_key` identifies a virtual or physical block range for a thin device. The comments define the key semantic: bios in the same overlapping cell are detained until unlock, preventing conflicting operations from running concurrently.

The API separates cell allocation from insertion so callers can avoid allocation under locks or in constrained contexts. `dm_get_cell()` retrieves/creates without a bio; `dm_bio_detain()` atomically retrieves/creates and appends a bio if the cell already exists; release variants expose holder/inmate control.

The header also declares deferred-set primitives used by thin/cache code to hold pending work behind outstanding operations. Its comments document the core safety reason: avoid installing a new mapping until prior reads of the old shared block have completed.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v1.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v2.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v2.c

Implements a v2 bio-prison with shared and exclusive lock semantics over the same style of overlapping range keys. The prison stores a workqueue pointer, spinlock, rb-tree, and mempool-backed cells.

`dm_cell_get_v2()` grants shared access unless an exclusive lock exists at an equal or higher level; blocked bios are appended to the cell. Shared users must call `dm_cell_put_v2()`, which decrements `shared_count`, may queue a quiesce continuation, and frees the cell if no exclusive owner remains.

`dm_cell_lock_v2()` obtains an exclusive cell lock. Existing exclusive lock returns `-EBUSY`; existing shared users cause a positive return indicating quiescing is needed. `dm_cell_quiesce_v2()` either queues the continuation immediately or stores it until shared users drain. `dm_cell_lock_promote_v2()` raises an exclusive lock level and again reports whether quiescing is needed.

`dm_cell_unlock_v2()` merges detained bios into the caller list, clears exclusive state if shared users remain, or erases the cell and returns ownership for freeing. The code notes two limitations: shared locks granted above an exclusive level can starve quiescing, and the implementation cannot yet track individual shared lock levels, so exclusive acquisition quiesces all shared holders.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v2.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v2.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v2.h

Declares the v2 bio-prison interface. Compared with v1, cells carry `exclusive_lock`, `exclusive_level`, `shared_count`, a quiesce continuation, rb-tree node, key, and detained bio list.

The API models two lock families. Shared locks are associated with bios and may be granted immediately or detained; callers drop them via `dm_cell_put_v2()`. Exclusive locks are bio-less, have lock levels, receive priority, and can force quiescing before work proceeds.

Return values are part of the contract: shared get returns true when granted; exclusive lock/promote return `<0` for error, `0` for locked without quiescing, and `1` for locked with quiescing required. Unlock returns whether the caller regains cell ownership and should free it.

The prison must be globally initialized with `dm_bio_prison_init_v2()` and torn down with `dm_bio_prison_exit_v2()`, while each prison instance is created with a workqueue used for deferred continuations.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v2.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-bio-record.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-bio-record.h

Provides tiny inline helpers for saving and restoring mutable `struct bio` fields. This is used by Device Mapper targets, such as multipath, that may resubmit a bio after lower block-layer code has modified its state.

`struct dm_bio_details` captures the target block device, remaining count, flags, iterator, end_io callback, and optional integrity payload. `dm_bio_record()` copies these from a bio before submission.

`dm_bio_restore()` writes the saved fields back, including resetting `__bi_remaining` atomically and restoring integrity metadata when `CONFIG_BLK_DEV_INTEGRITY` is enabled. The file is header-only and intentionally narrow.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-bio-record.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-bufio.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-bufio.c

Implements Device Mapper's buffered I/O cache library. A `dm_bufio_client` owns rb-tree indexed buffers, clean/dirty LRU lists, reserved buffers, a dm-io client, shrinker integration, and per-client locking. Each `dm_buffer` tracks block number, data allocation mode, hold count, dirty/write ranges, read/write state bits, errors, and optional debug stack traces.

Memory policy limits global cached bytes by RAM/vmalloc percentages, retains a configurable minimum, ages out old buffers, and triggers background replacement work when global allocation exceeds the cache limit. Buffer data may come from a slab cache, `__get_free_pages`, or `vmalloc`, selected by block size and allocation constraints.

Lookup/new/read paths use the rb-tree and LRU lists under the client mutex. `dm_bufio_get()` returns only an existing non-reading buffer; `dm_bufio_read()` allocates and reads; `dm_bufio_new()` allocates fresh without disk read; `dm_bufio_prefetch()` submits asynchronous reads. Allocation is failure-tolerant through reserved buffers, reclaiming unheld buffers, and waiting on a free-buffer queue.

Writeback tracks partial dirty byte ranges and aligns writes to 4 KiB. Small direct-mapped buffers use bios; vmalloc or too-large buffers fall back to dm-io. Dirty writes can be launched async, then synchronously waited and followed by a device flush. Discard and flush helpers issue dm-io operations directly.

Lifecycle code creates per-client slab caches, reserved buffers, dm-io client, shrinker, and global client registration. Destroy flushes/drops buffers, unregisters shrinkers, checks leaks, and frees caches. Module init creates the global workqueue and periodic cleanup; exit cancels work and BUGs on leaked clients or allocated memory.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-bufio.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-builtin.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-builtin.c

Contains `dm_kobject_release()`, a tiny helper compiled into the kernel rather than the loadable DM module. The long file comment explains a module-unload race if the kobject release method lived in unloadable module text.

The race occurs when an external kobject reference delays release until after the DM device teardown waits on completion, the module unloads, and the delayed releaser resumes execution in freed module code. Keeping the release callback built-in avoids that executable-text lifetime problem.

The implementation simply calls `complete(dm_get_completion_from_kobject(kobj))` and exports the symbol for DM code.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-builtin.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-background-tracker.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-background-tracker.c

Implements a tracker for cache policy background work. It wraps `policy_work` in `bt_work`, maintains queued and issued lists, and uses an rb-tree keyed by origin block to prevent duplicate pending work for the same oblock.

The tracker counts pending promotions, writebacks, and demotions with atomics and enforces `max_work` before allocating from a `bt_work` slab cache. `btracker_queue()` inserts work into the pending rb-tree and either returns it as already issued via `pwork` or appends it to the queued list.

`btracker_issue()` moves queued work to issued; `btracker_complete()` updates stats, erases the pending rb-node, removes the list node, and frees the work object. Duplicate oblocks return `-EINVAL`; no available work returns `-ENODATA`; capacity/allocation failures return `-ENOMEM`.

The header comment notes lack of locking; callers are expected to serialize access, which the SMQ policy does with its policy spinlock.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-background-tracker.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-background-tracker.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-background-tracker.h

Declares the background tracker used by cache policies. The API creates/destroys a tracker, queries queued writeback/demotion counts, queues work, issues queued work, completes issued work, and tests whether a promotion for an origin block is already pending.

The queue contract distinguishes duplicate work from allocation/capacity failure: `-EINVAL` means already queued, while `-ENOMEM` means it could not be queued for another reason. `btracker_issue()` returns `-ENODATA` when no work is available.

The file deliberately forward-declares tracker internals and includes `dm-cache-policy.h` for `struct policy_work` and block types. A FIXME explicitly calls out that locking semantics are undocumented.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-background-tracker.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-block-types.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-block-types.h

Defines sparse-distinct block identifier types for cache code: `dm_oblock_t` for origin blocks, `dm_cblock_t` for cache blocks, and `dm_dblock_t` for discard bitset blocks.

The inline conversion helpers use `__force` casts to move between raw integer/block types and the annotated types. This lets sparse catch accidental mixing of origin, cache, and discard indexes.

The file depends on persistent-data `dm_block_t` and keeps the type layer small and header-only.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-block-types.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-metadata.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-metadata.c

Implements persistent metadata for the DM cache target. The on-disk superblock stores checksum, flags, version, policy name/version/hint size, roots for mapping/hint/discard/dirty structures, cache geometry, feature flags, and statistics. Supported metadata versions are 1 and 2; v2 stores dirty bits in a separate disk bitset instead of in mapping flags.

The metadata object owns a block manager, transaction manager, metadata space map, dm-array mapping/hint metadata, discard and dirty bitsets, superblock-derived roots, rwsem locking, reference counting, and fail/read-only state. A global table keyed by block device prevents multiple active metadata instances for the same metadata device during table reloads.

Open/format flow checks whether the superblock is all zeroes, formats if permitted, validates checksum/magic/version/features, opens transaction manager and space map roots, then clears the clean-shutdown flag at transaction start. Commits flush dirty/discard bitsets, pre-commit the transaction manager, save the space-map root, update all superblock fields, set or clear clean shutdown, commit, and begin a new transaction.

Mappings are stored in a dm-array indexed by cache block. Each 64-bit value packs origin block in the high 48 bits and flags in the low 16 bits. Public operations resize the cache only if truncated blocks are unmapped or clean, insert/remove mappings, load mappings into a policy, set dirty bits, load discards, update stats, write policy hints, and test whether all cache blocks are clean.

Crash semantics are conservative: if metadata was not cleanly shut down, loaded mappings and discards are treated as dirty/not discarded as appropriate. `NEEDS_CHECK` can be set in the superblock, read-only mode delegates to the block manager, and abort destroys/reopens persistent objects; if rollback fails, `fail_io` blocks all further operations except close.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-metadata.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-metadata.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-metadata.h

Declares the DM cache metadata API and feature constants. Metadata block size and maximum metadata device sectors are inherited from the metadata space map; devices larger than 16 GiB trigger a warning threshold.

The public API covers open/close, cache resize/size, discard bitset resize/load/set, mapping insert/remove/load, dirty bit import, statistics get/set, commit, free/total metadata block counts, dump, hint writing, all-clean checks, needs-check state, read-only/read-write state, and transaction abort.

Callback typedefs let callers stream discard and mapping records without exposing internal dm-array or bitset structures. `dm_cache_statistics` stores 32-bit read/write hit/miss counters persisted in the superblock.

Feature masks are ext-style compat/ro-compat/incompat placeholders and are currently all zero, so unsupported on-disk feature bits cause open failure according to the metadata implementation.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-metadata.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-policy-internal.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-policy-internal.h

Provides inline wrappers around the `dm_cache_policy` vtable for internal cache target use. Most wrappers directly dispatch to policy methods, while optional hooks have defaults: `lookup_with_work` falls back to `lookup`, `get_hint` returns 0, `tick` is skipped, config emission returns zero values, and setting an unsupported config returns `-EINVAL`.

Also defines bitset utility helpers used by policies: compute bitset byte size, allocate with `vzalloc`, clear with `memset`, and free with `vfree`.

The header declares policy lifecycle helpers implemented in `dm-cache-policy.c`: create by name, destroy with module reference release, and query policy name/version/hint size. It is the bridge between the public policy interface and core target internals.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-policy-internal.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-policy-smq.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-policy-smq.c

Implements the stochastic multi-queue (`smq`) cache replacement policy plus `mq`, `cleaner`, and `default` registrations. It uses compact indexed `entry` objects instead of pointers: entries carry hash/list links, level, dirty/allocated/sentinel/pending flags, and origin block.

Core data structures include indexed intrusive lists, multi-level queues, hash tables for cache and hotspot lookup, entry allocators, clean/dirty/cache/hotspot queues, hit bitsets, confidence stats, rotating sentinels, and a background work tracker. The hotspot queue tracks larger origin regions to decide promotion candidates; clean and dirty queues track actual cache residency.

Lookup first checks the cache hash table, requeues hits upward once per period, and returns the cache block. Misses update the hotspot queue; if the hotspot entry reaches read/write promotion thresholds, the policy queues promotion work. If no cache entries are free, promotion attempts can trigger demotion work to maintain free space.

Background work includes promotions, demotions, and writebacks. Promotions reserve a cache entry immediately and complete by either installing it into hash/queue or freeing it on failure. Demotions remove clean entries on success or requeue them on failure. Writebacks clear pending state and requeue entries, while dirty/clean transitions move entries between dirty and clean queues.

Periodic `tick()` rotates writeback/demotion sentinels, clears hit bitsets, redistributes queue levels, resets stats, and adjusts hotspot promotion aggressiveness. `cleaner` disables migrations, making the policy focus on writeback/cleaning behavior. `mq` is an alias-compatible mode that accepts old tunables but warns they no longer have effect.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-policy-smq.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-policy.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-policy.c

Implements the registry for DM cache policy plugins. A global spinlock protects a list of `dm_cache_policy_type` records. Registration rejects duplicate names and only accepts hint sizes of 0 or 4 bytes.

Policy lookup first searches the in-memory registry and takes the owner module reference with `try_module_get()`. If absent, it calls `request_module("dm-cache-%s", name)` and retries. Creation calls the policy type's `create()` method and stores the type pointer in `policy->private`.

Destruction calls the policy object's destroy method and releases the module reference. Query helpers return the effective policy name, version, and hint size; aliases report their real policy name when `type->real` is set.

The file exports register/unregister/create/destroy/query symbols for policy modules and cache core code.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-policy.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-policy.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-policy.h

Defines the public cache policy interface. `enum policy_operation` and `struct policy_work` describe migration work requested by policies: promote, demote, or write back an origin/cache block pair.

`struct dm_cache_policy` is a vtable embedded in policy-specific objects. It supports lookup, optional immediate lookup-with-work, background work issue/complete, dirty state updates, initial mapping load, mapping invalidation, hint retrieval, residency reporting, optional periodic ticks, config emission/set, and migration enable/disable.

`struct dm_cache_policy_type` describes a registered policy module: name, version, optional alias target, hint size, owner module, and create callback. Names are limited to 16 bytes and versions to three integers.

The comments define important behavioral contracts: lookup must not block; background completion must use the original work pointer; hints are per-cache-block policy state; and policy registration is separate from policy object lifetime.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-cache-policy.h -->