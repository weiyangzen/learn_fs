# subset-b-006175 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/osd_client.c -->
# sources/distributed-fs/ceph-client/net/ceph/osd_client.c

## Purpose
`osd_client.c` is the kernel libceph OSD request engine. It builds MOSDOp requests, maps object locators through the current OSD map, owns per-OSD messenger sessions, submits and retries requests, processes OSD replies, handles OSD map changes, manages watch/notify linger requests, tracks OSD backoff ranges, and provides sparse-read receive support to the messenger. It is the integration point between CephFS/RBD/RADOS callers and the lower messenger/auth/monitor/map machinery.

## Important APIs, types, and functions
- Public request construction and lifecycle APIs include `ceph_osdc_alloc_request()`, `ceph_osdc_new_request()`, `ceph_osdc_alloc_messages()`, `ceph_osdc_start_request()`, `ceph_osdc_wait_request()`, `ceph_osdc_cancel_request()`, `ceph_osdc_sync()`, `ceph_osdc_get_request()`, and `ceph_osdc_put_request()`.
- Operation setup helpers populate `struct ceph_osd_req_op`: `osd_req_op_init()`, `osd_req_op_extent_init()`, `osd_req_op_extent_update()`, `osd_req_op_extent_dup_last()`, `osd_req_op_cls_init()`, `osd_req_op_xattr_init()`, `osd_req_op_alloc_hint_init()`, `osd_req_op_copy_from_init()`, and the `*_osd_data_*()` helpers for pages, bios, bvecs, pagelists, and iterators.
- `struct ceph_osd_client` holds the current `ceph_osdmap`, OSD session tree, linger request trees, map-check trees, request counters, mempools, message pools, and workqueues. Its synchronization root is `osdc->lock`, a read/write semaphore.
- `struct ceph_osd` models one OSD session: messenger connection, request/linger rbtrees, backoff trees, LRU state, auth handshake state, keepalive list node, and sparse-read receive state.
- `struct ceph_osd_request_target` records base and target object identifiers, current raw PG and actual shard PG, up/acting sets, selected OSD, pool flags, pause state, epoch, and resend markers.
- Linger/watch public APIs include `ceph_osdc_watch()`, `ceph_osdc_unwatch()`, `ceph_osdc_notify()`, `ceph_osdc_notify_ack()`, `ceph_osdc_list_watchers()`, and `ceph_osdc_flush_notifies()`.
- OSD map and cluster-state entry points include `ceph_osdc_handle_map()`, `ceph_osdc_maybe_request_map()`, `ceph_osdc_update_epoch_barrier()`, `ceph_osdc_abort_requests()`, `ceph_osdc_clear_abort_err()`, and `ceph_osdc_reopen_osds()`.
- Messenger integration is through `osd_con_ops`, with callbacks for allocation, dispatch, fault handling, sparse reads, auth handshake, reencoding, signing, and signature verification.

## Control flow
Request setup starts with allocation from the request slab/mempool or a flexible allocation for larger operation arrays. Callers initialize operation descriptors and attach data buffers, then allocate request and reply `ceph_msg` objects. `ceph_osdc_new_request()` also maps file layout offsets into object names and object extents using Ceph layout math, fills `r_base_oid` and `r_base_oloc`, and records snap/write metadata.

Submission flows through `ceph_osdc_start_request()` -> `submit_request()` -> `__submit_request()`. `__submit_request()` calls `calc_target()` against the current OSD map, creates or looks up the target `struct ceph_osd`, assigns a monotonically increasing TID atomically with request linking, and either sends, pauses, map-checks, or completes with an error. Writes are paused on full or `PAUSEWR` maps unless force flags allow them; reads are paused on `PAUSERD`; requests can also be held behind an epoch barrier.

`send_request()` refuses to send if the request falls inside an installed OSD backoff range. Otherwise it revokes any old queued message, sets retry/redirect flags, encodes MOSDOp front data in `encode_request_partial()`, records send timing, assigns the TID to the message header, and queues the message on the OSD connection. `encode_request_finish()` runs later from the messenger to append peer features for modern OSDs or reencode the front into a pre-luminous v4 layout when needed.

Reply handling uses `get_reply()` during receive allocation to find the registered request by TID and either reuse or resize the preallocated reply message. `handle_reply()` decodes `MOSDOpReply`, rejects mismatched retry attempts, handles redirect and read-replica `-EAGAIN` by resubmitting, validates operation counts and data length, records per-op return values and out lengths, finishes the request, and invokes completion inline. Decode or consistency failure completes with `-EIO`.

OSD map handling begins in `osd_dispatch()` for `CEPH_MSG_OSD_MAP`. `ceph_osdc_handle_map()` validates FSID, applies sequential incremental maps when possible, otherwise takes the newest full map, scans all requests and linger requests for target changes, closes sessions whose OSD went down or address changed, kicks resends, updates monitor subscriptions, aborts write requests when `ABORT_ON_FULL` applies, and wakes authentication waiters. Pool deletion uncertainty is resolved with async monitor version checks (`send_map_check()` and `send_linger_map_check()`).

Linger/watch flow allocates a `ceph_osd_linger_request`, registers it in client and OSD rbtrees, sends a watch/notify registration request, waits for commit, and then maintains state across map changes and connection faults. Watch notifications are decoded in `handle_watch_notify()` and queued to `notify_wq`; disconnect/error callbacks are normalized and also queued. Periodic timeout work sends watch pings to validate committed watches.

Backoff control decodes `MOSDBackoff` messages into hobject ranges per spg. Block messages install ranges and ACK the OSD; unblock messages remove ranges and attempt to resend matching requests that are no longer plugged. Connection faults clear all backoffs for that OSD and resubmit pending work.

Sparse reads are stateful across the messenger data cursor. `osd_sparse_read()` alternates through header, extent-count, extent-array, data-length, and data states; it zero-fills holes in the caller buffer, exposes extent data receive lengths to the messenger, and stores decoded sparse extent arrays back onto the matching OSD op.

## State and persistence behavior
State is in memory only. Persistent cluster truth comes from monitor-delivered OSD maps and OSD replies, but this file itself maintains no on-disk state. Major mutable structures are rbtrees keyed by TID, OSD id, linger id, spgid, hobject range, and backoff id. Request references are managed with `kref`; OSD sessions with `refcount_t`; linger requests with `kref`. Request data ownership varies by data type and `own_pages`/`pages_from_pool` flags, so release paths must mirror initialization.

The client schedules two delayed works: request/keepalive timeout scanning and idle OSD-session cleanup. `ceph_osdc_stop()` destroys workqueues, cancels delayed works, closes sessions, validates empty trees and counters, then destroys map, pools, and mempools.

## Dependencies and integration points
This file depends directly on `osdmap.c` APIs for pool lookup, object-to-PG mapping, acting/up set calculation, primary shard selection, and OSD map decoding. It uses `striper.c` through layout calculations for file-backed object requests. It uses `pagelist.c` and `pagevec.c` for encoded payloads and reply buffers, `snapshot.c` for snap context references, and `string_table.c` through pool namespace references in `ceph_object_locator`. It integrates with monitor client map subscriptions and version checks, messenger connection operations, auth client authorizers/signatures, debugfs state dumps, and higher CephFS/RBD callers through exported libceph APIs.

## Risks and edge cases
- Lock ordering is subtle: `osdc->lock`, per-OSD `mutex`, request-tree spinlock paths for sparse reads, and linger mutexes interact with callbacks and workqueues.
- Resend decisions depend on exact PG split, up/acting change, force-resend epoch, pool full, pause, and replica-read state; a missed condition can produce stale reads or writes sent to the wrong primary.
- Data ownership is mixed across pages, pagelists, bios, bvecs, and iov_iters. Incorrect `own_pages` or mempool flags can leak pages or double-free.
- Wire compatibility is broad: MOSDOp v8/v4 reencoding, reply v4+ decode, watch notify versions, object locator redirects, and messenger v2 addressing all need regression coverage.
- Sparse-read cursor state is per OSD connection and tied to matching request/op indexes; receive aborts and connection faults must reset it to avoid corrupting later replies.
- Backoff ranges are sorted by hobject identity and scoped to spgid; PG split or malformed ranges can plug or unblock too much work.
- Full/nearfull handling and `ABORT_ON_FULL` affect user-visible errors and cap-release epoch barriers.

## Test signals
Useful tests include OSD read/write request submission with map changes, pool deletion while requests are pending, full cluster/pool behavior with and without `ABORT_ON_FULL`, replica-read fallback on `-EAGAIN`, redirect replies, OSD connection fault/resend behavior, watch registration/reconnect/ping/notify/disconnect flows, list-watchers decode, class method calls, copy-from payload construction, sparse-read replies with holes and multiple ops, big-endian sparse extent conversion, and backoff block/unblock messages. Kernel sanitizers and lockdep are particularly valuable for this file because many correctness failures are lifetime or locking bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/osd_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/osdmap.c -->
# sources/distributed-fs/ceph-client/net/ceph/osdmap.c

## Purpose
`osdmap.c` decodes and owns the in-kernel representation of Ceph OSD maps and CRUSH maps, then answers placement questions for libceph clients. It maps objects to raw PGs, raw PGs to actual PGs, PGs to up and acting OSD sets, and PGs to primaries or erasure-coded shards. It also manages pool metadata, OSD state arrays, primary affinity, temporary mappings, upmap overrides, CRUSH location parsing, and incremental map application.

## Important APIs, types, and functions
- Map lifecycle APIs are `ceph_osdmap_alloc()`, `ceph_osdmap_decode()`, `osdmap_apply_incremental()`, and `ceph_osdmap_destroy()`.
- Pool lookup helpers are `ceph_pg_pool_by_id()`, `ceph_pg_pool_name_by_id()`, `ceph_pg_poolid_by_name()`, and `ceph_pg_pool_flags()`.
- Object identity helpers include `ceph_oloc_copy()`, `ceph_oloc_destroy()`, `ceph_oid_copy()`, `ceph_oid_printf()`, `ceph_oid_aprintf()`, and `ceph_oid_destroy()`.
- Placement APIs include `ceph_object_locator_to_pg()`, `__ceph_object_locator_to_pg()`, `ceph_pg_to_up_acting_osds()`, `ceph_pg_to_primary_shard()`, and `ceph_pg_to_acting_primary()`.
- Interval-change helpers include `ceph_pg_compare()`, `ceph_spg_compare()`, `ceph_pg_is_split()`, `ceph_is_new_interval()`, `ceph_osds_changed()`, and `ceph_osds_copy()`.
- CRUSH locality APIs include `ceph_parse_crush_location()`, `ceph_compare_crush_locs()`, `ceph_clear_crush_locs()`, and `ceph_get_crush_locality()`.
- Core data structures are `struct ceph_osdmap`, `struct ceph_pg_pool_info`, `struct ceph_pg_mapping`, `struct ceph_osds`, `struct ceph_object_locator`, `struct ceph_object_id`, `struct workspace_manager`, and decoded CRUSH map/bucket/rule structures.

## Control flow
Full map decode starts with wrapper/client-data version parsing in `get_osdmap_client_data_v()`. `osdmap_decode()` then reads FSID, epoch, timestamps, pools, pool names, pool max, flags, max OSD, OSD state/weight/address arrays, `pg_temp`, `primary_temp`, primary affinity, CRUSH payload, and optional upmap structures. It allocates and resizes arrays through `osdmap_set_max_osd()` and installs a decoded CRUSH map through `osdmap_set_crush()`, which also seeds the CRUSH workspace manager.

Incremental decode in `osdmap_apply_incremental()` validates the next epoch, handles embedded full maps, optionally replaces CRUSH, updates flags/pool max/max OSD, applies new/removed pools and names, applies OSD up/state/weight changes in a deliberate order, and then updates temporary mappings, primary affinity, erasure-code profile skips, and upmap changes. `decode_new_up_state_weight()` first scans encoded sections, applies new weights, then state xors, then up-client addresses so cases that both mark an OSD up and remove existence land in the intended final state.

CRUSH decode in `crush_decode()` validates magic, allocates buckets/rules, decodes bucket algorithms, names, tunables, class metadata skips, and choose-arg maps. `crush_finalize()` calculates per-map workspace size. Placement later borrows workspaces from `workspace_manager`, allocating up to roughly one per online CPU and otherwise waiting for an idle workspace.

Object-to-PG mapping starts in `__ceph_object_locator_to_pg()`, which hashes either object name alone or namespace plus separator plus object name. `raw_pg_to_pg()` stable-mods the raw seed to the pool PG count. `raw_pg_to_pps()` derives the placement seed, either using `HASHPSPOOL` hashing or legacy pool-plus-seed arithmetic.

PG-to-OSD mapping starts with `pg_to_raw_osds()`: find a CRUSH rule for pool ruleset/type/size, run CRUSH with the placement seed and pool-specific choose args, and remove nonexistent OSDs. `apply_upmap()` applies exact `pg_upmap` and item replacement overrides while ignoring targets marked out. `raw_to_up_osds()` removes down OSDs or substitutes `CRUSH_ITEM_NONE` depending on replicated versus erasure-coded pool behavior. `apply_primary_affinity()` probabilistically chooses a different primary when configured. `get_temp_osds()` overlays `pg_temp` and `primary_temp` to produce the acting set. `ceph_pg_to_up_acting_osds()` composes those steps and validates the result.

CRUSH locality parsing stores user-specified type/name pairs in an rbtree. Locality lookup walks upward from an OSD through CRUSH bucket membership using a linear parent search and returns the closest matching bucket type id, or `-1` if no requested location matches.

## State and persistence behavior
All map state is in memory and replaced or mutated from monitor-provided binary maps. `struct ceph_osdmap` owns arrays for OSD state, weights, addresses, optional primary affinity, rbtrees for pools and PG mappings, the CRUSH map, and CRUSH workspaces. Pool names and object ids may allocate dynamic memory; object locators hold refcounted `ceph_string` namespaces. Destroy paths empty every rbtree, release CRUSH and workspace memory, and `kvfree()` array allocations.

## Dependencies and integration points
`osd_client.c` relies on this file for every target recalculation and resend decision. The file depends on Ceph decode helpers for wire-format bounds checking, CRUSH mapper/hash code for placement, rbtree helper macros for ordered maps, `string_table.c` for pool namespace references, messenger address decoders for OSD address vectors, and CephFS/RBD callers through exported object locator and placement APIs.

## Risks and edge cases
- Decode is compatibility-heavy; wrong version handling or skipped-field length handling can corrupt the cursor and poison the map.
- `osdmap_set_max_osd()` resizes several parallel arrays; partial allocation or primary-affinity resizing failures need careful cleanup expectations.
- Incremental map ordering is security and correctness sensitive because state, weight, and address sections can conflict.
- Placement behavior differs for replicated pools that can shift OSDs and erasure-coded pools that preserve shard positions with `CRUSH_ITEM_NONE`.
- Upmap item replacement explicitly does not support bidirectional swaps; tests should lock in that behavior.
- Primary affinity changes the order of replicated up sets and must stay consistent with interval-change detection in `osd_client.c`.
- CRUSH locality parent lookup is linear and ambiguous for items present in multiple buckets.
- `ceph_oid_printf()` BUGs when formatted names do not fit inline storage; callers with unbounded names must use `ceph_oid_aprintf()`.

## Test signals
High-value tests include decoding full maps and incremental maps across supported struct versions, resizing `max_osd`, adding/removing pools, pool name lookup, OSD up/down/exists/weight transitions, primary affinity decode and placement effects, `pg_temp` and `primary_temp`, `pg_upmap` and `pg_upmap_items`, replicated versus erasure-coded acting set behavior, PG split detection, object namespace hashing, CRUSH choose args, fallback choose args, address-vector decode under msgr2, malformed map bounds checks, and CRUSH location parse/compare/locality cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/osdmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/pagelist.c -->
# sources/distributed-fs/ceph-client/net/ceph/pagelist.c

## Purpose
`pagelist.c` implements `struct ceph_pagelist`, a reference-counted list of pages used as a growable encoded byte buffer for Ceph messages. It is used when request metadata or payload fragments need to be appended incrementally without requiring one contiguous allocation.

## Important APIs, types, and functions
- `ceph_pagelist_alloc()` allocates and initializes the page list, free reserve list, length/room counters, mapped tail pointer, and refcount.
- `ceph_pagelist_release()` drops a reference, unmaps the tail page, frees all active pages, frees reserved pages, and releases the container.
- `ceph_pagelist_append()` appends bytes across page boundaries, allocating or consuming reserved pages as needed.
- `ceph_pagelist_reserve()` preallocates enough pages to satisfy a future append without allocation.
- `ceph_pagelist_free_reserve()` frees all unused reserved pages.
- `ceph_pagelist_addpage()` and `ceph_pagelist_unmap_tail()` are internal helpers for page management and `kmap()`/`kunmap()` state.

## Control flow
Allocation starts with an empty active page list and zero room, so the first append enters the while loop, copies zero bytes if no room is available, calls `ceph_pagelist_addpage()`, maps the new page, and then copies data to `mapped_tail`. Longer appends copy up to the current room, allocate a new page when room is insufficient, and continue until all bytes are appended.

Reservation computes the number of pages beyond current room needed for a future byte count and fills `free_list` with `__page_cache_alloc(GFP_NOFS)` pages. `ceph_pagelist_addpage()` prefers reserved pages before allocating. Release unmaps any mapped tail before freeing active pages, then frees reserves.

## State and persistence behavior
The pagelist is strictly in-memory. Persistent state consists only of `length`, `room`, active page order, reserve page count, and the currently mapped tail address. The active pages store encoded wire data until the owning Ceph message consumes or releases the pagelist. Reference counting allows multiple users to retain the same pagelist, as seen in notify resend paths.

## Dependencies and integration points
The file depends on Linux page allocation, highmem mapping, list manipulation, and Ceph pagelist declarations. Inline encoding helpers in `pagelist.h` build on `ceph_pagelist_append()`. `osd_client.c` uses pagelists for class request info, xattr payloads, notify payloads, notify ACKs, and other encoded request data.

## Risks and edge cases
- `ceph_pagelist_append()` assumes `mapped_tail` is valid once nonzero data is copied; callers rely on `ceph_pagelist_addpage()` before the final copy when room was initially insufficient.
- Pointer arithmetic on `const void *buf` is a GNU C kernel extension.
- Highmem mappings must be balanced; forgetting `ceph_pagelist_unmap_tail()` would leak mappings.
- Reserve accounting must stay exact; `BUG_ON(pl->num_pages_free)` catches mismatches only at reserve-free time.
- Allocation uses `GFP_NOFS`, appropriate for filesystem paths but still failure-prone under memory pressure.

## Test signals
Tests should cover zero-length append, single-page append, cross-page append, append after reserve, reserve larger than room, release with mapped tail, release with active and reserved pages, reference count retention, and encoded integer/string helpers from `pagelist.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/pagelist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/pagevec.c -->
# sources/distributed-fs/ceph-client/net/ceph/pagevec.c

## Purpose
`pagevec.c` provides small exported helpers for allocating, releasing, dirtying, copying from, and zeroing vectors of `struct page *` used by Ceph message payloads and replies.

## Important APIs, types, and functions
- `ceph_alloc_page_vector()` allocates an array of page pointers and fills it with newly allocated page-cache pages.
- `ceph_release_page_vector()` frees pages that were allocated by Ceph and then frees the pointer array.
- `ceph_put_page_vector()` drops caller-held page references and optionally marks pages dirty before `put_page()`.
- `ceph_copy_from_page_vector()` copies bytes from a page vector into a linear buffer starting at a page-relative offset.
- `ceph_zero_page_vector_range()` zeros a byte range spanning one or more pages.

## Control flow
Allocation first creates the pointer array, then loops page-by-page. If any page allocation fails, it releases the pages already allocated and returns `ERR_PTR(-ENOMEM)`. Copying and zeroing both compute page offset from the caller-provided range, then walk pages until the byte count is exhausted. Dirty release loops pages and calls `set_page_dirty_lock()` before `put_page()` when requested.

## State and persistence behavior
The vector is in-memory ownership state only. Callers choose between freeing allocated pages (`ceph_release_page_vector()`) and putting referenced pages (`ceph_put_page_vector()`). Zeroing mutates page contents, and dirtying marks pages for writeback through normal kernel page-cache mechanisms.

## Dependencies and integration points
This file depends on Linux page allocation, page dirtying, `zero_user_segment()`, and Ceph allocation helpers. `osd_client.c` uses it for reply buffers, notify IDs, list-watchers, copy-from payload pages, and sparse/read data buffers. Higher CephFS code uses page vectors for file IO paths.

## Risks and edge cases
- Callers must use the correct release function for owned allocated pages versus referenced page-cache pages.
- `ceph_copy_from_page_vector()` starts from `pages[0]` plus `off & ~PAGE_MASK`; it expects the page vector itself to already be aligned to the logical range.
- Zeroing and copying assume the range fits the provided vector; there is no local bounds check.
- `page_address()` requires pages that are directly addressable in this kernel configuration.

## Test signals
Exercise partial-first-page copy, full-page copy, multi-page copy, leading and trailing zero ranges, allocation failure cleanup, dirty versus non-dirty put behavior, and ownership handoff from OSD reply paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/pagevec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/snapshot.c -->
# sources/distributed-fs/ceph-client/net/ceph/snapshot.c

## Purpose
`snapshot.c` implements the reference-counted `ceph_snap_context` helper used by libceph and CephFS to carry snapshot sequence metadata and an inline array of snapshot ids for reads and writes.

## Important APIs, types, and functions
- `ceph_create_snap_context()` allocates one object sized for `struct ceph_snap_context` plus `snap_count` inline snap ids, initializes `nref` to one, and records `num_snaps`.
- `ceph_get_snap_context()` increments the refcount when passed a non-NULL context.
- `ceph_put_snap_context()` decrements the refcount and frees the context when it reaches zero.

## Control flow
Creation computes the variable-length allocation size, uses `kzalloc()` with caller-provided GFP flags, sets the reference count, and leaves sequence and snap array contents for the caller to fill. Get/put are thin refcount wrappers and tolerate NULL in the put path.

## State and persistence behavior
Snapshot context state is entirely in-memory but represents durable Ceph snapshot ordering observed elsewhere. The helper owns only allocation and lifetime; callers own the meaning and initialization of `seq` and `snaps[]`.

## Dependencies and integration points
`osd_client.c` stores a referenced snap context in write requests and encodes `snap_seq` plus snap ids into MOSDOp requests. CephFS address-space and snapshot code also share contexts for dirty pages and writeback.

## Risks and edge cases
- Integer overflow in size computation would be serious if `snap_count` were not bounded by upstream protocol/caller constraints.
- Callers must fill `seq` and `snaps[]`; creation intentionally does not validate semantic ordering.
- Refcount misuse can leak or prematurely free contexts shared by in-flight OSD requests.

## Test signals
Tests should cover zero-snapshot allocation, multi-snapshot allocation, get/put lifetime, NULL get/put behavior where applicable, and request encoding that includes expected snapshot sequence and ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/snapshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/string_table.c -->
# sources/distributed-fs/ceph-client/net/ceph/string_table.c

## Purpose
`string_table.c` implements a global intern table for `struct ceph_string`, primarily used for pool namespace strings. Interning lets locators and layouts share equal strings with refcounted lifetime and RCU-safe delayed freeing.

## Important APIs, types, and functions
- `ceph_find_or_create_string()` looks up an existing interned string by length/content, takes a reference if still alive, or allocates and inserts a new string.
- `ceph_release_string()` removes a string from the rbtree if still linked and frees it with `kfree_rcu()`.
- `ceph_strings_empty()` reports whether the global string tree has no entries.
- The implementation uses global `string_tree` and `string_tree_lock`.

## Control flow
Lookup first searches under the spinlock. If it finds a matching node but `kref_get_unless_zero()` fails, the dying node is erased and lookup proceeds as a miss. On miss, the function allocates a new flexible string object, initializes its kref and NUL-terminated contents, then retries insertion under the lock. A concurrent insertion wins by freeing the new object and returning the existing referenced string. A concurrent dying match is erased and the insertion loop retries.

Release runs from `kref_put()` callbacks. It erases the node from the global rbtree if present, clears the rb node, drops the lock, then uses `kfree_rcu()` so RCU readers using `ceph_try_get_string()` can safely observe disappearing pointers.

## State and persistence behavior
The intern table is process-global in kernel memory and persists until all references are dropped. Strings are ordered by length then content using `ceph_compare_string()`. There is no on-disk state. `ceph_strings_empty()` is useful as a leak/test signal but is lockless, so it is best interpreted when no concurrent users remain.

## Dependencies and integration points
`ceph_object_locator` holds `struct ceph_string *pool_ns`. `osdmap.c` copies/destroys locators and object layout pool namespaces through string-table refcounts. CephFS inode layouts and OSD request target copying use these strings across RCU-protected paths.

## Risks and edge cases
- Correctness relies on `kref_get_unless_zero()` to avoid resurrecting strings that are in release.
- Global spinlock contention can appear if namespace churn is high, though expected cardinality is low.
- `ceph_strings_empty()` does not take the spinlock.
- Comparison sorts by length before bytes, which is fine for an internal tree but must remain consistent with all lookup/insert paths.

## Test signals
Test duplicate lookup returning the same object, concurrent create races, release removing a node, retry after dying-node detection, RCU-safe delayed freeing through `ceph_try_get_string()`, empty string interning, and final `ceph_strings_empty()` after all puts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/string_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/striper.c -->
# sources/distributed-fs/ceph-client/net/ceph/striper.c

## Purpose
`striper.c` maps Ceph file byte ranges to RADOS object extents and maps object extents back to file extents according to `struct ceph_file_layout`. It encapsulates stripe unit, stripe count, object size, object set, and object-number arithmetic used by CephFS IO and OSD request construction.

## Important APIs, types, and functions
- `ceph_calc_file_object_mapping()` maps a file offset/length to object number, object offset, and contiguous bytes within the current stripe unit.
- `ceph_file_to_extents()` maps a file range to a sorted list of merged `struct ceph_object_extent` records, allocating new extents through a caller callback and invoking an action callback per stripe-unit segment.
- `ceph_iterate_extents()` repeats the file-to-object walk against an already populated extent list and invokes the action callback for containing extents.
- `ceph_extent_to_file()` reverse maps an object range to one or more file extents.
- `ceph_get_num_objects()` computes the number of objects needed to cover a file size.

## Control flow
`ceph_calc_file_object_mapping()` divides the file offset by stripe unit to get global block number and block offset, divides block number by stripe count to get stripe number and stripe position, divides stripe number by stripes-per-object to get object set number and position, then derives object number and object offset. It caps mapped length to the remainder of the stripe unit.

`ceph_file_to_extents()` loops through the requested file range one stripe unit at a time. For each segment it looks up the last extent for the object number. If the new segment is contiguous with the previous object extent, it extends that record; otherwise it asks the caller to allocate a new extent and inserts it in sorted object order. A final validation pass warns and fails if the list is unsorted or overlapping.

`ceph_iterate_extents()` performs the same mapping loop without allocation; every computed object segment must be contained in the provided list. `ceph_extent_to_file()` computes the number of stripe-unit intersections covered by an object range, allocates that many `ceph_file_extent` records, and reconstructs file offsets from object number, object offset, stripe position, and object set number.

## State and persistence behavior
The file itself is stateless. It computes deterministic mappings from a supplied `ceph_file_layout`. Callers own all extent lists and allocated reverse-mapping arrays.

## Dependencies and integration points
`osd_client.c` uses layout calculation when building object requests from file offsets. CephFS read/write paths depend on these mappings to split file IO into object IO. The file depends on Linux 64-bit division helpers and Ceph layout/type declarations.

## Risks and edge cases
- Layout fields must be valid: zero stripe unit, zero stripe count, or object size not divisible by stripe unit would break division or mapping assumptions.
- Extent merging assumes successive calls map sorted file ranges into a shared object extent list.
- Reverse mapping allocation size depends on `objoff + objlen` and stripe unit math; very large ranges need overflow awareness.
- `ceph_get_num_objects()` has nontrivial remainder logic for partially used final object sets.

## Test signals
Test single-object layouts, multi-object stripe counts, multi-stripe objects, unaligned offsets, ranges crossing stripe-unit boundaries, ranges crossing object boundaries, merge behavior for adjacent object segments, sorted-list validation, reverse mapping round trips, zero-length reverse mapping, and object count calculations at exact period and partial-period boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ceph/striper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/compat.c -->
# sources/distributed-fs/ceph-client/net/compat.c

## Purpose
`compat.c` implements 32-bit compatibility handling for socket syscalls on 64-bit kernels. It translates 32-bit user `msghdr` and ancillary data layouts into native kernel forms, translates native control messages back into 32-bit layout, handles SCM_RIGHTS fd delivery, and exposes compat socket syscall wrappers including legacy `socketcall`.

## Important APIs, types, and functions
- `__get_compat_msghdr()` copies fields from an already loaded `compat_msghdr` into a kernel `msghdr`, clamps name length, sets control-user state, and optionally saves the user address pointer.
- `get_compat_msghdr()` copies the user header, calls the internal converter, and imports the compat iovec into `msg_iter`.
- `cmsghdr_from_user_compat_to_kern()` walks 32-bit control messages, computes native control length, allocates stack or socket memory, and copies/realigns ancillary records.
- `put_cmsg_compat()` writes a native control message into the caller's 32-bit control buffer, including old 32-bit timeval/timespec conversion when required.
- `scm_detach_fds_compat()` installs received file descriptors into the compat user's SCM_RIGHTS buffer and truncates when the buffer cannot hold all fds.
- Compat syscall wrappers dispatch `sendmsg`, `sendmmsg`, `recvmsg`, `recv`, `recvfrom`, `recvmmsg_time64`, optional `recvmmsg_time32`, and legacy `socketcall`.

## Control flow
Input message conversion copies the compat header from user memory, normalizes absent names to zero length, rejects negative name length and too many iovecs, imports iovecs as source or destination depending on receive/send context, and leaves control data marked as user-backed until ancillary conversion is requested.

Ancillary input conversion first validates every compat cmsg and accumulates the native aligned length. It then uses the provided stack buffer or `sock_kmalloc()`, copies each cmsg header and data payload into native `cmsghdr` layout, and only publishes `kmsg->msg_control` and native `msg_controllen` after the full conversion succeeds. Failure frees any socket allocation and returns `-EFAULT`, `-EINVAL`, or `-ENOMEM`.

Ancillary output conversion checks remaining user control space, converts old timestamp control payloads for 32-bit time ABIs, writes a `compat_cmsghdr`, copies payload data, sets `MSG_CTRUNC` when short, and advances `msg_control_user`/`msg_controllen`.

`socketcall` validates the subcall number, copies the expected number of 32-bit arguments, audits them, and dispatches to native socket helpers with pointer arguments passed through `compat_ptr()`. Individual compat syscall wrappers mostly call native `__sys_*` helpers with `MSG_CMSG_COMPAT` added to flags.

## State and persistence behavior
The file maintains no durable state. It mutates per-call `msghdr` cursors, flags, control pointers, and SCM cookies. Received fds installed by `scm_detach_fds_compat()` become normal process file descriptors; the SCM cookie is destroyed after detaching.

## Dependencies and integration points
This is generic networking compatibility code, not Ceph-specific. It depends on Linux compat types, uaccess helpers, socket core helpers, audit hooks, SCM fd helpers, timestamp ABI definitions, and native socket syscall implementations. The file lives under the same source tree subset but integrates with the kernel network syscall layer.

## Risks and edge cases
- Cmsg length validation and alignment are security-sensitive because they parse user-controlled buffers.
- Integer truncation between compat sizes and native sizes can corrupt cursor arithmetic if checks regress.
- `put_cmsg_compat()` copies only the truncated payload length after setting `MSG_CTRUNC`; callers must tolerate partial ancillary messages.
- Time conversion depends on `COMPAT_USE_64BIT_TIME` and old timestamp cmsg types.
- `scm_detach_fds_compat()` must avoid leaking file references when the user buffer is too small or fd installation fails.
- `socketcall` argument count table must match legacy syscall numbering.

## Test signals
Test valid and malformed compat msghdrs, boundary `msg_namelen`, excessive iovec counts, empty and invalid cmsg buffers, multiple cmsg realignment, stack versus socket allocation paths, timestamp cmsg conversion, short control buffers setting `MSG_CTRUNC`, SCM_RIGHTS delivery with too few slots, all compat syscall wrappers adding `MSG_CMSG_COMPAT`, and legacy `socketcall` dispatch/audit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/compat.c -->
