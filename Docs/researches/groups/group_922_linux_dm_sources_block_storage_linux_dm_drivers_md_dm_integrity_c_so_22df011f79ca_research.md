# Group Research: Device Mapper integrity, I/O, ioctl, copy, linear, and userspace log sources

This group covers Linux Device Mapper integrity-tag storage, shared DM I/O helpers, control-plane ioctl dispatch, asynchronous copy/zero service, the linear target, and userspace dirty-log transport/integration.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-integrity.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-integrity.c

## Purpose
Implements the Device Mapper `integrity` target. It stores and verifies per-block integrity tags either supplied through block-integrity payloads or generated internally with a hash/MAC. It supports direct writes, journaled writes, bitmap write tracking, recovery mode, optional metadata device separation, journal encryption/MAC, discard handling, and background tag recalculation.

## Main Interfaces
- Target lifecycle: `dm_integrity_ctr()`, `dm_integrity_dtr()`, `dm_integrity_postsuspend()`, `dm_integrity_resume()`.
- I/O path: `dm_integrity_map()`, `dm_integrity_map_continue()`, `integrity_end_io()`, `integrity_metadata()`.
- Journal handling: `write_journal()`, `replay_journal()`, `do_journal_write()`, `init_journal()`, `__journal_read_write()`.
- Metadata/tag access: `get_metadata_sector_and_offset()`, `dm_integrity_rw_tag()`, `integrity_sector_checksum()`.
- Bitmap/recalculation: `block_bitmap_op()`, `bitmap_block_work()`, `bitmap_flush_work()`, `integrity_recalc()`.
- Reporting and limits: `dm_integrity_status()`, `dm_integrity_iterate_devices()`, `dm_integrity_io_hints()`.

## Control Flow
Construction parses the target line `<dev> <start> <tag_size|-> <mode> <feature args>`, opens the data and optional metadata devices, reads or initializes the superblock, computes journal/metadata geometry, creates workqueues, dm-io and dm-bufio clients, optional crypto transforms, journal memory, bitmap state, and recalculation buffers.

`dm_integrity_map()` validates bounds, block alignment, integrity-payload size, mode restrictions, flush/FUA semantics, and maps the logical sector to data and metadata locations. Flushes are deferred to commit handling. Normal I/O is passed to `dm_integrity_map_continue()`.

In journal mode, writes reserve journal entries under `endio_wait.lock`, copy data and tags into the in-memory journal, and later commit journal sections to disk. Reads first check whether a newer block exists in the journal tree and can be served from the journal. A writer workqueue later copies committed journal entries to the data device and persists tags.

In direct and bitmap modes, bios go to the data device while tag verification or tag writes happen through metadata work. Reads with internal hashes and discards may be forced through synchronous offloaded paths so metadata checks or updates happen after the underlying bio completes.

Background recalculation scans data, reads blocks, computes tags, writes metadata, and advances `sb->recalc_sector`. Bitmap mode uses on-disk bitmap blocks in the journal area to remember regions needing recalculation or delayed write permission, then flushes and clears bitmap state when safe.

## State And Synchronization
`struct dm_integrity_c` owns target geometry, devices, dm-io/dm-bufio clients, superblock, journal page lists, crypto state, tag hash/MAC specs, workqueues, journal ring positions, range locks, bitmap pages, recalculation buffers, flush lists, timers, and failure/mismatch counters.

`endio_wait.lock` protects overlapping in-progress ranges, waiters, flush lists, and journal allocation state. An rb-tree tracks active ranges to prevent overlapping metadata/data updates. A second rb-tree maps logical sectors to journal entries. Workqueues separate metadata hashing, waiting/offload, commit, writer, and recalc work. Failure is latched in `ic->failed` and propagated to later bios.

## Integration Points
Uses Device Mapper target hooks, `dm_io` for synchronous/asynchronous metadata and journal I/O, `dm_bufio` for tag blocks, Linux crypto shash/skcipher APIs for internal hashes and journal protection, block-integrity registration when tags are externally supplied, audit logging for MAC/checksum failures, and reboot notifiers to force synchronous bitmap flushing before shutdown.

## Notable Behaviors
- Modes are `J` journaled, `B` bitmap, `D` direct, and `R` recovery/read-only style mode.
- `internal_hash` disables external integrity payloads and generates tags from sector number plus data.
- `journal_crypt` can use full skcipher operation or precomputed XOR stream for byte-granular ciphers.
- `journal_mac` protects journal section metadata; `fix_hmac` adds salt and fixed HMAC behavior in newer superblock versions.
- Recalculation with keyed HMAC is blocked unless `legacy_recalculate` is specified, because regenerating tags can weaken authenticity assumptions.
- FUA writes are completed only after the target’s required metadata/journal flush path runs.
- Discards are only allowed with internal hashes and mark tags with a discard filler.
- Bitmap mode sets `SB_FLAG_DIRTY_BITMAP` on resume and clears it during clean suspend after flushing.

## Risks And Review Focus
- Journal commit ordering is durability-critical: entries must not be exposed as committed before copied data, tags, MACs, and flushes are ordered correctly.
- The range rb-tree and wait-list logic is central to avoiding overlapping journal replay, recalc, discard, and normal I/O races.
- Superblock version/flag compatibility affects padding, MAC behavior, separate metadata devices, bitmap state, and recalculation.
- Tag comparison allows discard filler as a special case; review paths that mix discard, internal hashes, and partial tag comparisons carefully.
- Error latching means one failed metadata, crypto, MAC, or I/O path changes behavior for all later bios.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-integrity.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-io-tracker.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-io-tracker.h

## Purpose
Defines a small inline helper for tracking in-flight I/O sectors and how long a device has been idle.

## Main Interfaces
- `dm_iot_init()` initializes the lock, zero in-flight count, and time fields.
- `dm_iot_idle_for()` reports whether there has been no in-flight I/O for at least a requested jiffies interval.
- `dm_iot_idle_time()` returns the current idle duration when idle.
- `dm_iot_io_begin()` adds sectors to the in-flight count.
- `dm_iot_io_end()` subtracts sectors and records `idle_time` when the count reaches zero.

## Control Flow
Callers increment the tracked sector count when I/O begins and decrement it when I/O completes. Idle queries take the spinlock, check for zero in-flight sectors, and compare current `jiffies` against the recorded idle timestamp.

## State And Synchronization
`struct dm_io_tracker` stores a spinlock, `in_flight` sector count, `idle_time`, and `last_update_time`. All public operations take the spinlock with IRQ-safe variants where needed. `last_update_time` is initialized but not otherwise used in this header.

## Integration Points
This is a header-only utility intended for DM targets or helpers that need cheap idle detection without owning a larger accounting subsystem.

## Notable Behaviors
- `dm_iot_io_end()` ignores zero-length completions.
- Idle time is only meaningful after the in-flight count reaches zero.
- There is no underflow protection beyond caller correctness.

## Risks And Review Focus
- Callers must pair begin/end sector counts exactly.
- Any future use of `last_update_time` must preserve the current lock discipline.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-io-tracker.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-io.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-io.c

## Purpose
Implements the exported `dm_io()` helper used by DM targets to issue synchronous or asynchronous I/O to one or more block-device regions from several memory source types.

## Main Interfaces
- Client lifecycle: `dm_io_client_create()`, `dm_io_client_destroy()`.
- I/O submission: `dm_io()`.
- Module setup: `dm_io_init()`, `dm_io_exit()`.
- Internal dispatch: `sync_io()`, `async_io()`, `dispatch_io()`, `do_region()`.
- Memory adapters: page-list, bio, vmalloc/VMA, and kernel-memory `dpages` implementations.

## Control Flow
A caller supplies a `dm_io_request`, region array, operation, flags, memory description, optional callback, and optional error bitmap. `dm_io()` initializes a `dpages` adapter for the supplied memory type. Without a callback it performs synchronous I/O and waits for completion; with a callback it submits asynchronously.

`dispatch_io()` iterates regions, rewinding the page iterator for each region, and calls `do_region()`. `do_region()` splits requests into bios based on remaining sectors, page availability, operation type, and queue limits. Completion records region error bits and invokes the final callback when the aggregate atomic count reaches zero.

## State And Synchronization
Each `dm_io_client` owns a mempool of aligned `struct io` objects and a bioset. `struct io` tracks the aggregate completion count, error bits, callback, context, and VMA invalidation info. The region index is packed into low alignment bits of `bio->bi_private` alongside the `struct io` pointer.

## Integration Points
Used by DM targets for metadata, journal, copy, flush, and data movement I/O. It integrates with block-layer bios, queue limits for discard/write-zeroes/write-same, vmalloc cache flush/invalidate helpers, and DM reserved bio counts.

## Notable Behaviors
- Multi-region reads are rejected; multi-region I/O is only allowed for writes.
- Read errors zero-fill the bio before completion.
- VMA reads invalidate the kernel vmap range after completion.
- Discard, write zeroes, and write same requests are split according to device limits and fail with `BLK_STS_NOTSUPP` if unsupported.
- Asynchronous callers are warned in comments to use `REQ_SYNC` or unplug later to avoid delayed dispatch.

## Risks And Review Focus
- The pointer-plus-region packing depends on `struct io` alignment and `DM_IO_MAX_REGIONS`.
- The memory adapters assume caller-provided buffers cover the requested byte count.
- Multi-region write error bits must be interpreted by the caller.
- Special command splitting depends on current queue limits and can produce zero-bvec bios.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-io.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ioctl.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-ioctl.c

## Purpose
Implements the `/dev/mapper/control` ioctl interface for Device Mapper. It creates, removes, renames, suspends, resumes, loads tables, reports status/dependencies, sends messages, lists devices/target versions, supports polling, and provides early-boot DM creation.

## Main Interfaces
- Control file operations: `dm_open()`, `dm_release()`, `dm_poll()`, `dm_ctl_ioctl()`.
- Device hash management: `dm_hash_insert()`, `dm_hash_rename()`, `dm_hash_remove_all()`, `dm_deferred_remove()`.
- Device commands: `dev_create()`, `dev_remove()`, `dev_rename()`, `dev_suspend()`, `dev_status()`, `dev_wait()`.
- Table commands: `table_load()`, `table_clear()`, `table_deps()`, `table_status()`.
- Message/version/list commands: `target_message()`, `list_devices()`, `list_versions()`, `get_target_version()`.
- Interface setup: `dm_interface_init()`, `dm_interface_exit()`.
- Utilities exported/early: `dm_copy_name_and_uuid()`, `dm_early_create()`.

## Control Flow
`ctl_ioctl()` checks `CAP_SYS_ADMIN`, validates the ioctl type and DM interface version, looks up the command handler, copies and validates the user parameter block, runs the selected handler, optionally issues a global event, copies results back, and wipes secure buffers when requested.

Mapped devices are indexed by name and UUID rb-trees, each entry holding the `mapped_device` and an optional inactive table. Create allocates a DM device and inserts a hash cell. Table load builds a new inactive `dm_table`, validates queue type/immutable target constraints, measures it for IMA, and stages it in the hash cell. Resume swaps the inactive table into the live table, updates read-only state, resumes the device, destroys the old table, and emits uevents.

Status and dependency queries retrieve either the live or inactive table under SRCU and serialize target data into the ioctl result buffer. Target messages with `@` prefixes are handled by DM core; other messages are routed to the target covering the supplied sector.

## State And Synchronization
Global name and UUID rb-trees are protected by `_hash_lock`. `dm_hash_cells_mutex` protects mdptr-to-hash-cell name/UUID access. Live tables are protected by DM’s SRCU table access rules. Device queue type changes are serialized with `dm_lock_md_type()`. Per-open `struct dm_file` stores the global event number used by poll.

## Integration Points
This file bridges user space and DM core: mapped device allocation/destruction, table construction, target type registry, stats messages, IMA measurement, uevents, misc device registration, compat ioctl handling, and global event polling.

## Notable Behaviors
- Lookup accepts exactly one identifier: UUID, name, or device number; UUID wins only when supplied alone.
- `DM_SECURE_DATA_FLAG` causes the user buffer and kernel copy to be wiped.
- `DM_DEFERRED_REMOVE` can mark busy devices for later removal.
- `DM_QUERY_INACTIVE_TABLE_FLAG` switches status/dependency queries to the staged inactive table.
- Remove-all loops until no more progress is possible because mapped devices can depend on other mapped devices.
- Early boot creation bypasses normal ioctl serialization by receiving target specs and parameter strings directly.

## Risks And Review Focus
- User-buffer sizing and alignment are security-sensitive, especially variable-length status, dependency, and list responses.
- The `_hash_lock` and SRCU table lifetime comments are important; destroying tables while a live-table reference is held can deadlock.
- Rename and UUID-setting paths mutate hash-cell strings under mixed rwsem/mutex protection.
- Resume error paths must correctly destroy or preserve inactive/live tables.
- Target messages can return data through the ioctl buffer, so buffer-full detection must be honored.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-kcopyd.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-kcopyd.c

## Purpose
Implements DM kcopyd, an asynchronous block copy/zero service used by DM targets to copy one source region to one or more destination regions, split large jobs, throttle copy I/O, and report completion through callbacks.

## Main Interfaces
- Global setup: `dm_kcopyd_init()`, `dm_kcopyd_exit()`.
- Client lifecycle: `dm_kcopyd_client_create()`, `dm_kcopyd_client_destroy()`, `dm_kcopyd_client_flush()`.
- Work submission: `dm_kcopyd_copy()`, `dm_kcopyd_zero()`.
- Callback-only helpers: `dm_kcopyd_prepare_callback()`, `dm_kcopyd_do_callback()`.

## Control Flow
A client owns reserved pages, a `dm_io_client`, a job mempool, a workqueue, and four job lists. `dm_kcopyd_copy()` allocates one master job plus split-job storage, configures source/destinations, decides whether sequential writes are required for host-managed zoned destinations, and dispatches either one job or multiple sub-jobs.

Copy jobs first acquire pages, then issue a read from the source, then write the pages to all destinations. Zero jobs use `WRITE_ZEROES` when all destinations support it, otherwise write from a reusable zero page list. Completion moves jobs through callback/complete queues so final callbacks run from kcopyd’s workqueue context.

## State And Synchronization
`struct dm_kcopyd_client` contains page accounting, a job spinlock, callback/complete/io/pages lists, throttle pointer, workqueue, destroy waitqueue, and active-job counter. Split jobs share a master job mutex, progress counter, write offset, and aggregate error state. Throttle accounting is protected by a global spinlock.

## Integration Points
Uses `dm_io()` for block I/O, DM module parameters for sub-job sizing, block zoned-device model checks, block write-zeroes support checks, mempools for no-I/O allocation safety, and workqueues for serialized callback execution.

## Notable Behaviors
- Default sub-job size is 512 KiB, capped at 1024 KiB by module parameter handling.
- Large jobs are split into `SPLIT_COUNT` concurrent sub-jobs.
- Host-managed zoned destinations force sequential writes and disable ignore-error behavior.
- Throttling tracks approximate busy versus total periods and sleeps in 100 ms increments, bounded by `MAX_SLEEPS`.
- Client destruction waits for all submitted jobs before freeing resources.

## Risks And Review Focus
- Split-job lifetime depends on the mempool object containing the master plus sub-job array.
- Sequential write ordering relies on `write_offset` and `pop_io_job()` choosing only the next eligible write.
- Ignored errors and normal errors take different completion paths; callers must understand read versus per-destination write error reporting.
- Throttle accounting is global-lock based and approximate, so changes can affect copy-rate behavior across clients.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-kcopyd.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-linear.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-linear.c

## Purpose
Implements the simple Device Mapper `linear` target, which maps a contiguous logical range to a contiguous range on one underlying block device.

## Main Interfaces
- Target lifecycle: `linear_ctr()`, `linear_dtr()`.
- I/O mapping: `linear_map()`, `linear_map_bio()`, `linear_map_sector()`.
- Reporting/control: `linear_status()`, `linear_prepare_ioctl()`, `linear_iterate_devices()`.
- Zoned/DAX support: `linear_report_zones()`, `linear_dax_direct_access()`, `linear_dax_zero_page_range()`.
- Module hooks: `dm_linear_init()`, `dm_linear_exit()`.

## Control Flow
Construction parses `<dev_path> <offset>`, opens the underlying device with the table mode, stores the start sector, and advertises flush/discard/secure-erase/write-same/write-zeroes support pass-through counts. Mapping replaces the bio device and offsets the sector by `start + target_offset`, except for zero-sector bios unless they are zone-management operations.

## State And Synchronization
The target context is only `struct linear_c`, containing the underlying `dm_dev` and start sector. It relies on DM core table/device lifetime rules rather than internal locking.

## Integration Points
Passes through integrity and crypto capabilities via target feature flags, supports nowait, host-managed zoned devices, block ioctl pass-through when the mapping exactly covers the whole device, and DAX direct access/zeroing when filesystem DAX is enabled.

## Notable Behaviors
- `prepare_ioctl` only permits ioctl pass-through if the linear mapping starts at zero and length equals the underlying device size.
- `iterate_devices` exposes the exact underlying range for queue-limit stacking.
- IMA status emits device name and start sector.
- DAX page offsets are adjusted by the underlying block device start sector.

## Risks And Review Focus
- Sector arithmetic is intentionally minimal; constructor validation of start-sector parsing matters.
- Zone-management bios require sector remapping even if they carry no data sectors.
- Capability pass-through assumes the underlying device and table stacking code enforce detailed limits.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-linear.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-log-userspace-base.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-log-userspace-base.c

## Purpose
Implements the DM dirty-log type `userspace`, allowing mirror/replication dirty-log decisions to be delegated to a userspace log server through the userspace-log transfer layer.

## Main Interfaces
- Dirty-log lifecycle: `userspace_ctr()`, `userspace_dtr()`, `userspace_presuspend()`, `userspace_postsuspend()`, `userspace_resume()`.
- Region queries: `userspace_is_clean()`, `userspace_in_sync()`, `userspace_is_remote_recovering()`.
- Region mutation: `userspace_mark_region()`, `userspace_clear_region()`, `userspace_set_region_sync()`.
- Resync/status: `userspace_get_resync_work()`, `userspace_get_sync_count()`, `userspace_status()`.
- Flush handling: `userspace_flush()`, `flush_by_group()`, `flush_one_by_one()`, `do_flush()`.
- Module setup: `userspace_dirty_log_init()`, `userspace_dirty_log_exit()`.

## Control Flow
Construction expects a UUID, optional `integrated_flush`, and userspace-implementation-specific arguments. It builds a constructor string beginning with target length, sends `DM_ULOG_CTR` to userspace, retrieves region size, optionally opens a returned log device, initializes flush-entry mempool state, and creates a delayed flush workqueue when integrated flush is enabled.

Mark and clear operations enqueue flush entries under `flush_lock`. `userspace_flush()` detaches local mark/clear lists, sends clear requests first, then mark requests and a final flush. Requests are grouped up to `MAX_FLUSH_GROUP_COUNT`; failed grouped sends fall back to one-by-one sends. Integrated flush sends mark groups as `DM_ULOG_FLUSH` payloads and delays clear-only flushes.

Most dirty-log operations call `userspace_do_request()`, which retries server communication after `-ESRCH` by periodically attempting a new constructor request and then resume.

## State And Synchronization
`struct log_c` stores the DM target, optional log device, constructor string, region geometry, local unique ID, UUID, mark/clear lists, in-sync hint, optional delayed flush workqueue, integrated-flush flag, and flush-entry mempool. `flush_lock` protects pending mark/clear lists. `sched_flush` tracks whether delayed flush work is pending.

## Integration Points
Registers as a `dm_dirty_log_type`, uses `dm_consult_userspace()` from the transfer layer, opens devices returned by userspace through DM table device management, emits table events on log failures, and participates in target status output.

## Notable Behaviors
- The local unique ID is derived from the `log_c` pointer value.
- `in_sync_hint` is reset on resume and used to reduce remote-recovery traffic once earlier regions are known in sync.
- `userspace_in_sync()` returns `-EWOULDBLOCK` when asked not to block.
- Failed `is_clean`, `in_sync`, and sync-count requests choose conservative results.
- `clear_region` is allowed to fail allocation and skip clearing, causing extra future resync rather than unsafe cleanliness.
- Status info falls back to `COM_FAILURE` on userspace communication failure.

## Risks And Review Focus
- Kernel/userspace protocol failures are treated differently by operation; conservative defaults must match mirror correctness expectations.
- Integrated flush changes ordering and batching semantics, especially delayed clear-only flushes.
- The reconnect loop can block while repeatedly trying to contact userspace.
- Grouped request payload size is bounded by transfer-layer preallocation, so batching constants must stay compatible.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-log-userspace-base.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-log-userspace-transfer.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-log-userspace-transfer.c

## Purpose
Implements the connector/netlink transport used by DM userspace dirty logs. It serializes requests to a userspace log server, waits for matching replies, retries on timeout or `-EAGAIN`, and copies response payloads back to callers.

## Main Interfaces
- Request API: `dm_consult_userspace()`.
- Transport lifecycle: `dm_ulog_tfr_init()`, `dm_ulog_tfr_exit()`.
- Internal send/receive: `dm_ulog_sendto_server()`, `cn_ulog_callback()`, `fill_pkg()`.

## Control Flow
`dm_consult_userspace()` validates payload size against a 512-byte preallocated buffer, serializes request construction with `dm_ulog_lock`, fills a `dm_ulog_request`, assigns a sequence number, adds a stack-allocated receiving package to a global list, sends the connector message, and waits up to `DM_ULOG_RETRY_TIMEOUT`.

The connector callback receives ACKs or full replies, requires `CAP_SYS_ADMIN`, finds the waiting package by sequence number, records error/data, and completes the waiter. Timeouts and `-EAGAIN` responses resend the request with a new sequence.

## State And Synchronization
A global preallocated connector message/request buffer is protected by `dm_ulog_lock`. `receiving_list` stores currently waiting stack packages and is protected by `receiving_list_lock`. `dm_ulog_seq` monotonically assigns request sequence numbers.

## Integration Points
Uses Linux connector IDs `CN_IDX_DM` and `CN_VAL_DM_USERSPACE_LOG`, `cn_netlink_send()`, connector callback registration, and the public `dm_ulog_request` protocol definitions from `linux/dm-log-userspace.h`.

## Notable Behaviors
- Netlink/connector is treated as unreliable; timed-out requests are resent indefinitely.
- Late responses are discarded because their receiving package has already been removed.
- Response buffers are size-checked and fail with `-ENOSPC` if too small.
- The request structure is zeroed before filling to avoid leaking kernel memory to userspace.
- Only one request is sent at a time because the send buffer is global and preallocated.

## Risks And Review Focus
- The receiving list contains stack objects from sleeping callers; correctness depends on removing them before returning.
- Infinite retry behavior can hang callers if the userspace server stops responding without returning `-ESRCH`.
- Sequence number wrap is not specially handled.
- Capability checks in the callback guard message acceptance but depend on connector context semantics.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-log-userspace-transfer.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-log-userspace-transfer.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-log-userspace-transfer.h

## Purpose
Declares the internal transfer-layer API used by the userspace dirty-log implementation to initialize connector transport, shut it down, and send requests to userspace.

## Main Interfaces
- `dm_ulog_tfr_init()` initializes connector callback state and preallocated transport buffers.
- `dm_ulog_tfr_exit()` unregisters the connector callback and frees transport buffers.
- `dm_consult_userspace()` sends a typed request with optional payload and optional response buffer.

## Control Flow
The header contains no logic; it establishes the contract consumed by `dm-log-userspace-base.c` and implemented by `dm-log-userspace-transfer.c`.

## State And Synchronization
No state is declared here beyond the shared `DM_MSG_PREFIX` macro. Transport state is private to the `.c` implementation.

## Integration Points
Includes `uint64_t`/size-based request arguments and uses request type constants defined by the broader DM userspace-log interface.

## Notable Behaviors
- `rdata_size` is value-result style: input capacity and output used size.
- The UUID and local unique ID identify the userspace log instance for each request.

## Risks And Review Focus
- Callers must pass payload sizes compatible with the transfer implementation’s preallocated limit.
- Response-buffer ownership and lifetime remain with the caller.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-log-userspace-transfer.h -->