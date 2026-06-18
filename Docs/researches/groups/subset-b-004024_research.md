# Research Group: subset-b-004024

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-integrity.c -->
## sources/distributed-fs/ceph-client/drivers/md/dm-integrity.c

### Purpose
`dm-integrity.c` implements the Device Mapper `integrity` target. It adds per-block integrity tags to a mapped block device, optionally computes those tags internally with the kernel crypto API, and persists metadata either interleaved with data or on a separate metadata device. It supports direct metadata updates, journaled writes, bitmap mode, recovery-only mode, and inline block-integrity mode.

### Important APIs, Types, And Functions
The exported integration point is `integrity_target`, whose callbacks are `dm_integrity_ctr`, `dm_integrity_dtr`, `dm_integrity_map`, `dm_integrity_end_io`, `dm_integrity_postsuspend`, `dm_integrity_resume`, `dm_integrity_status`, `dm_integrity_iterate_devices`, and `dm_integrity_io_hints`. Module init/exit allocate `journal_io_cache` and register/unregister the target.

Key on-disk structures are `struct superblock`, `struct journal_entry`, and `struct journal_sector`. Important flags include `SB_FLAG_HAVE_JOURNAL_MAC`, `SB_FLAG_RECALCULATING`, `SB_FLAG_DIRTY_BITMAP`, `SB_FLAG_FIXED_PADDING`, `SB_FLAG_FIXED_HMAC`, and `SB_FLAG_INLINE`. Key in-memory structures are `struct dm_integrity_c` for target state, `struct dm_integrity_io` for per-bio state, `struct dm_integrity_range` for overlap exclusion, `struct journal_node` for the journal rbtree, and `struct bitmap_block_status` for bitmap-mode deferred writes.

The metadata geometry is calculated by `get_area_and_offset`, `get_metadata_sector_and_offset`, `get_data_sector`, `calculate_journal_section_size`, `calculate_device_limits`, and `get_provided_data_sectors`. Crypto/tag paths flow through `get_alg_and_key`, `get_mac`, `integrity_sector_checksum_*`, and `dm_integrity_rw_tag`. Journal paths use `write_journal`, `__journal_read_write`, `integrity_commit`, `do_journal_write`, `integrity_writer`, `replay_journal`, and `init_journal`. Recalculation is implemented by `integrity_recalc` and `integrity_recalc_inline`.

### Control Flow
Construction parses four required arguments (`device`, `start`, `tag size`, `mode`) and up to eighteen feature arguments, including `meta_device`, `block_size`, `journal_sectors`, `interleave_sectors`, `buffer_sectors`, `journal_watermark`, `commit_time`, `sectors_per_bit`, `bitmap_flush_interval`, `internal_hash`, `journal_crypt`, `journal_mac`, `recalculate`, `reset_recalculate`, `allow_discards`, `fix_padding`, `fix_hmac`, and `legacy_recalculate`. `dm_integrity_ctr` opens devices, validates crypto algorithms, allocates mempools, biosets, workqueues, superblock memory, dm-io and dm-bufio clients, journal pages, journal trees, and bitmap structures as required by mode.

`dm_integrity_map` rejects invalid alignment and bounds, validates external bio integrity payloads when no internal hash is used, strips FUA when it must be satisfied by metadata flushing, maps logical data sectors to backing sectors, and then dispatches to `dm_integrity_map_continue` or the inline path. In journal mode, writes reserve journal entries, place sectors in an rbtree for read-after-write lookup, copy data and tags into the in-memory journal, and queue commits based on free space or autocommit timers. Reads consult the journal tree first, then fall back to backing data plus tag verification. Bitmap mode uses journal sectors as a persistent dirty bitmap and defers writes until the relevant bitmap block is safely written. Direct mode writes metadata through dm-bufio while data I/O is submitted to the device. Inline mode attaches generated integrity payloads to the outgoing bio and validates them in `dm_integrity_end_io`.

Commit flow pads partial sections, waits for in-progress journal entries, stamps commit ids, calculates optional MAC/encryption, writes journal sections with FUA/SYNC, then later `integrity_writer` copies committed entries to final data/tag locations and frees journal space. Resume reads the superblock, replays journal or dirty bitmap state, updates geometry/recalculation flags, and starts recalculation work when needed. Postsuspend drains recalculation, commit, and writer workqueues, flushes buffers, clears journals/bitmaps when safe, and marks the journal uptodate.

### State And Persistence Behavior
Persistent state is dominated by the superblock, metadata tag blocks managed by dm-bufio, journal sections, commit ids, optional journal MACs, optional encrypted journal copies, and bitmap-mode dirty bitmaps. Runtime state includes `in_progress` range exclusion, `wait_list`, `journal_tree_root`, committed/uncommitted/free section counters, autocommit timer, mismatch counter, per-mode workqueues, and crypto/mempool resources. Recalculation advances `sb->recalc_sector` and periodically writes the superblock; bitmap mode mirrors dirty ranges between `journal`, `recalc_bitmap`, and `may_write_bitmap`.

### Dependencies And Integration Points
The file depends on Device Mapper core target registration, `dm_io`, `dm_bufio`, `dm-bio-record`, block integrity payloads, kernel crypto shash/ahash/skcipher APIs, async XOR, rbtrees, workqueues, timers, mempools, biosets, reboot notifiers, and DM audit/IMA status hooks. It integrates with block queue limits through `io_hints`, with DM table device iteration through `iterate_devices`, and with userspace status/table output through `status`.

### Risks And Edge Cases
High-risk areas are crash consistency of journal replay and bitmap flushes, concurrency between range exclusion and journal tree updates, memory pressure in crypto/recheck/recalc paths, correctness of metadata geometry for interleaved versus separate metadata devices, and handling of HMAC recalculation. The code intentionally disables some recalculation combinations unless `legacy_recalculate` is set. The inline write path contains a suspicious zero-length padding expression (`ic->tuple_size - ic->tuple_size`) where padding beyond `tag_size` appears intended. Journal encryption/MAC error handling sets the target failed state, so a single crypto or metadata error can poison later I/O. Discard handling is conditional on internal hashes and has special filler-tag semantics.

### Test Signals
Useful tests include dmsetup creation across modes `J`, `B`, `D`, `R`, and `I`; power-failure or forced-reload journal replay; dirty bitmap resume; recalculate/resume progression; external versus internal integrity payload validation; misaligned bio rejection; discard tag filler behavior; FUA/prefetch flush ordering; separate metadata-device sizing; encrypted/MAC journal configurations; and status output for mismatch counters and recalc sectors. Kernel selftests should exercise dm-crypt/dm-integrity stacking, suspend/resume, read-after-write before commit, and low-memory allocation fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-integrity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-io-rewind.c -->
## sources/distributed-fs/ceph-client/drivers/md/dm-io-rewind.c

### Purpose
`dm-io-rewind.c` reconstructs a `dm_io` original bio after partial splitting/advancement. It rewinds the bio iterator, integrity iterator, and inline encryption data unit number so Device Mapper can restore a fixed-end original bio when an I/O segment must be retried or reprocessed.

### Important APIs, Types, And Functions
The main exported-internal entry is `dm_io_rewind(struct dm_io *io, struct bio_set *bs)`. Helpers include `dm_bvec_iter_rewind`, `dm_bio_integrity_rewind`, `dm_bio_crypt_dun_decrement`, `dm_bio_crypt_rewind`, `dm_bio_rewind_iter`, and `dm_bio_rewind`. The implementation is conditional on `CONFIG_BLK_DEV_INTEGRITY` and `CONFIG_BLK_INLINE_ENCRYPTION`.

### Control Flow
`dm_io_rewind` clones `io->orig_bio` using `bio_alloc_clone`, calculates how many bytes the current original bio has advanced relative to `io->sector_offset`, rewinds the clone, trims it to `io->sectors`, chains it to the old original bio, compensates for `bio_chain` incrementing `__bi_remaining`, and replaces `io->orig_bio`.

The data iterator rewind moves `bi_sector` backward and either increases size for no-advance bios or walks backward through the bvec array, restoring `bi_idx` and `bi_bvec_done`. If integrity metadata is present, `dm_bio_integrity_rewind` converts completed data sectors to integrity intervals/bytes and rewinds `bip_iter`. If inline encryption is present, `dm_bio_crypt_rewind` decrements the DUN as a multi-limb integer by the number of completed encryption data units.

### State And Persistence Behavior
There is no persistent state. Runtime mutation is limited to the cloned bio's `bi_iter`, optional `bio_integrity_payload` iterator, optional `bio_crypt_ctx` DUN array, chaining state, and `io->orig_bio`. The original bio's completion reference count is adjusted after chaining.

### Dependencies And Integration Points
This file depends on block bio vectors, block integrity helpers, inline encryption context, and `dm-core.h`'s `struct dm_io`. It is tightly coupled to DM bio splitting because the caller must provide a bio with a fixed end sector and must restore size separately.

### Risks And Edge Cases
The core risk is rewinding beyond the beginning of the bvec array; this is guarded by `WARN_ONCE` and returns false internally, but `dm_bio_rewind` does not propagate a failure. Inline encryption correctness depends on `bytes` being aligned to the crypto data-unit size. Integrity rewind correctness depends on the block integrity profile for the target disk. Reference-count compensation around `bio_chain` is subtle and must match `dm_split_and_process_bio` behavior.

### Test Signals
Test with partially completed split bios, bios carrying integrity payloads, bios carrying inline encryption contexts, no-advance bio operations, multi-bvec bios, and boundary cases where rewinding crosses vector boundaries. Fault-injection tests should check warning behavior when invalid byte counts attempt to rewind past the original bvec range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-io-rewind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-io-tracker.h -->
## sources/distributed-fs/ceph-client/drivers/md/dm-io-tracker.h

### Purpose
`dm-io-tracker.h` provides a small inline helper for tracking in-flight sector counts and idle time for a Device Mapper component. It answers whether a device has been idle for a duration and records when I/O begins and ends.

### Important APIs, Types, And Functions
The only type is `struct dm_io_tracker`, containing a spinlock, `sector_t in_flight`, `idle_time`, and `last_update_time`. Inline APIs are `dm_iot_init`, `dm_iot_idle_for`, `dm_iot_idle_time`, `dm_iot_io_begin`, and `dm_iot_io_end`.

### Control Flow
Initialization sets up the spinlock, clears `in_flight` and `idle_time`, and records `last_update_time = jiffies`. `dm_iot_io_begin` adds a sector length under lock. `dm_iot_io_end` subtracts a nonzero sector length and, if the counter reaches zero, records the current `jiffies` as the idle start. Query functions take the same lock and return either elapsed idle jiffies or whether `jiffies` is after `idle_time + j`.

### State And Persistence Behavior
All state is volatile and in-memory. `in_flight` is sector-based, not bio-count-based, so callers must pass matching lengths to begin/end. `last_update_time` is initialized but not otherwise updated by these helpers in this version.

### Dependencies And Integration Points
The header depends on `linux/jiffies.h`, spinlocks, `sector_t`, and jiffies time comparison helpers. It is designed for inclusion by DM targets or core components that need low-overhead idle detection.

### Risks And Edge Cases
The helpers do not guard against underflow if callers end more sectors than they began. A zero-length end is ignored. Because `idle_time` is only meaningful when `in_flight` is zero, users must not inspect it without the helper or equivalent locking. IRQ-safe locking is used for query/end, while begin uses `spin_lock_irq`, so call sites should not already hold the same lock.

### Test Signals
Useful tests are balanced begin/end accounting, idle transition timing after the last end, no idle report while sectors remain in flight, zero-length end behavior, and jiffies wrap-safe comparisons through `time_after`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-io-tracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-io.c -->
## sources/distributed-fs/ceph-client/drivers/md/dm-io.c

### Purpose
`dm-io.c` implements the Device Mapper helper API for issuing synchronous or asynchronous I/O to one or more block regions from different memory sources. It is used by DM targets to read/write metadata, copy buffers, issue flushes, discards, write-zeroes, and collect per-region errors without open-coding bio allocation and completion tracking.

### Important APIs, Types, And Functions
Public APIs are `dm_io_client_create`, `dm_io_client_destroy`, `dm_io`, `dm_io_init`, and `dm_io_exit`. `struct dm_io_client` owns an I/O mempool and bioset. Internal `struct io` holds `error_bits`, an atomic completion count, callback/context, and optional vmalloc invalidation state. `struct dpages` abstracts page iteration for `DM_IO_PAGE_LIST`, `DM_IO_BIO`, `DM_IO_VMA`, and `DM_IO_KMEM`.

Important functions include `store_io_and_region_in_bio`/`retrieve_io_and_region_from_bio`, `complete_io`, `dec_count`, `endio`, the four dpages initializers, `do_region`, `dispatch_io`, `async_io`, `sync_io`, and `dp_init`.

### Control Flow
`dm_io` validates that multi-region operations are writes, initializes a `dpages` iterator from the caller's memory description, and chooses synchronous or asynchronous execution based on `io_req->notify.fn`. Asynchronous execution allocates `struct io` from a mempool, initializes its count to one, and dispatches one region at a time. Synchronous execution wraps asynchronous execution with a completion and `wait_for_completion_io`.

`do_region` splits a region into one or more bios. For discard and write-zeroes it checks device support and emits segment-sized command bios without data vectors. For data I/O it repeatedly asks `dpages` for pages, fills bios with `bio_add_page`, submits each bio, and increments the shared count before submission. `endio` zero-fills failed reads, decodes the packed region number from `bi_private`, drops the bio, and updates error bits. When the count reaches zero, `complete_io` invalidates vmapped read ranges if necessary, frees the `io`, and calls the client callback.

### State And Persistence Behavior
There is no persistent state. Runtime state is held in per-client pools and per-request `struct io`. Error state is returned as a bitset where each bit corresponds to a region. For VMA reads, the helper flushes the kernel vmap range before issuing I/O and invalidates it after completion.

### Dependencies And Integration Points
The file depends on Device Mapper core helpers, block bios, mempools, biosets, completions, `linux/dm-io.h`, and memory abstractions such as page lists, bio bvecs, vmalloc memory, and direct kernel memory. It is a shared service for many DM targets, including `dm-integrity.c` and `dm-kcopyd.c`.

### Risks And Edge Cases
The `struct io` pointer is packed with a region number in low pointer bits, so the alignment guarantee is critical and enforced with `BUG()`. Multi-region non-write I/O is rejected. Unsupported discard/write-zeroes returns `BLK_STS_NOTSUPP` through the normal completion path. Atomic writes warn if they cannot be submitted as a single bio. Failed reads are zero-filled, which is an intentional data safety behavior but can hide stale buffer contents in tests unless error bits are checked.

### Test Signals
Tests should cover synchronous and asynchronous callbacks, all memory types, multi-region writes with per-region error bits, unsupported discard/write-zeroes, flush-only zero-length regions, VMA cache maintenance, failed read zero-fill, bio splitting over multiple pages, and client create/destroy under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ioctl.c -->
## sources/distributed-fs/ceph-client/drivers/md/dm-ioctl.c

### Purpose
`dm-ioctl.c` implements the `/dev/mapper/control` userspace ABI for Device Mapper. It creates/removes/renames mapped devices, loads and swaps mapping tables, reports status/dependencies/target versions, sends target messages, waits and polls for events, and supports early-boot mapped-device creation.

### Important APIs, Types, And Functions
External entry points include `dm_interface_init`, `dm_interface_exit`, `dm_deferred_remove`, `dm_copy_name_and_uuid`, and `dm_early_create`. The miscdevice file operations are `_ctl_fops`, using `dm_open`, `dm_release`, `dm_poll`, `dm_ctl_ioctl`, and optional compat ioctl.

Important internal types are `struct dm_file` for poll state, `struct hash_cell` for name/uuid/device tracking plus an inactive `new_map`, and `struct vers_iter` for target-version listing. The two rbtrees `name_rb_tree` and `uuid_rb_tree` are protected by `_hash_lock`; `dm_hash_cells_mutex` protects `mdptr` name/uuid access.

Core operations include hash lookup/insert/remove/rename helpers, `dev_create`, `dev_remove`, `dev_rename`, `do_suspend`, `do_resume`, `table_load`, `table_clear`, `table_deps`, `table_status`, `target_message`, `lookup_ioctl`, `check_version`, `copy_params`, `validate_params`, and `ctl_ioctl`.

### Control Flow
`ctl_ioctl` requires `CAP_SYS_ADMIN`, validates the ioctl type, checks userspace ABI version while copying the kernel version back, maps the command number through `lookup_ioctl`, copies parameters into kernel memory, validates names/uuids and flags, calls the selected handler, optionally issues a global event, copies results back to userspace, and wipes secure buffers when requested.

Device creation validates names, optionally uses a persistent minor, calls `dm_create`, inserts a hash cell, and returns status. Removal locks a device for deletion, unlinks the hash cell, destroys any inactive table, emits IMA and uevents, and destroys the mapped device. Rename changes name or sets a UUID under the hash lock, emits table events and uevents, and measures through IMA.

Table load creates a `dm_table`, parses each `dm_target_spec` with strict alignment and NUL-termination checks, completes the table, checks immutable target and queue type constraints, sets up the queue on first load, and stages the table as `hc->new_map`. Resume optionally suspends, swaps `new_map` into the live table, updates disk read-only state, resumes the device, emits resize/change events, and destroys the old table after synchronization. Status and deps acquire live or inactive tables via SRCU and serialize results into the ioctl buffer.

### State And Persistence Behavior
The control plane maintains in-kernel rbtrees by name and uuid, references on `mapped_device`, inactive tables staged per hash cell, per-open poll event snapshots, and global event notifications. It does not persist mappings by itself; persistence is userspace policy. `DM_SECURE_DATA_FLAG` causes copied ioctl buffers to be wiped before return/free. Early boot creation bypasses normal serialized ioctl payloads by accepting prebuilt target spec/parameter arrays, but still creates a device, inserts it in the hash, builds a table, swaps it live, and resumes it.

### Dependencies And Integration Points
This file integrates with DM core (`dm_create`, `dm_destroy`, `dm_suspend`, `dm_resume`, `dm_table_*`, `dm_swap_table`, `dm_get_live_table`, `dm_get_mdptr`), target registry iteration, DM stats messages, IMA measurement hooks, kobject uevents, miscdevice registration, Linux usercopy, capabilities, polling, SRCU table lifetime rules, and block device geometry/read-only state.

### Risks And Edge Cases
The ABI parser is security-sensitive: `data_size`, `data_start`, target `next` offsets, alignment, and NUL termination must be checked exactly to avoid overreads or corrupt target loading. Hash locking is subtle because table destruction waits for live table references and must not happen under `_hash_lock` in paths that could deadlock. `find_device` returns an `md` with a reference acquired by hash lookup; every path must balance `dm_put`. `DM_SECURE_DATA_FLAG` must wipe both user and kernel buffers. Race-prone areas include deferred removal, rename versus lookup, inactive table replacement, suspend failure rollback, and uevent/global-event generation.

### Test Signals
Tests should cover all ioctl commands, invalid version negotiation, invalid names and uuid/name conflicts, buffer-full reporting, secure-data wiping, target spec alignment and missing NULs, inactive table load/clear/resume rollback, immutable target rejection, deferred remove cancellation, event wait/poll behavior, status/deps output against live and inactive tables, target messages with DM-core `@` commands, compat ioctl paths, and early boot create failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-kcopyd.c -->
## sources/distributed-fs/ceph-client/drivers/md/dm-kcopyd.c

### Purpose
`dm-kcopyd.c` provides the Device Mapper asynchronous copy/zero service used by targets that need to copy one block-device region to one or more destinations. It handles page buffering, job splitting, write ordering for zoned devices, throttling, and completion callbacks.

### Important APIs, Types, And Functions
Public APIs are `dm_kcopyd_init`, `dm_kcopyd_exit`, `dm_kcopyd_client_create`, `dm_kcopyd_client_destroy`, `dm_kcopyd_client_flush`, `dm_kcopyd_copy`, `dm_kcopyd_zero`, `dm_kcopyd_prepare_callback`, and `dm_kcopyd_do_callback`. `kcopyd_subjob_size_kb` is a module parameter bounded by `dm_get_kcopyd_subjob_size`.

Important structures are `struct dm_kcopyd_client`, which owns reserved pages, a `dm_io_client`, job mempool, workqueue, throttle, job count, waitqueue, and four job lists; and `struct kcopyd_job`, which stores source/destination regions, pages, operation, error state, callback, split-job progress, sequential write offset, and master-job linkage.

### Control Flow
Client creation initializes job lists, a job mempool sized for `MIN_JOBS`, a reclaim-safe per-CPU workqueue, reserved pages sized from the subjob limit, a dm-io client, and a destroy waitqueue. Copy submission allocates one master job plus `SPLIT_COUNT` subjobs from the slab mempool, records source/destinations and flags, auto-enables sequential writes for host-managed zoned destinations, disables ignore-error when sequential ordering is required, and either dispatches a single job or seeds split subjobs through `segment_complete`.

The worker `do_work` always processes completions first, then page allocation jobs, then I/O jobs. Page jobs allocate temporary pages or fall back to the reserved pool. I/O jobs call `dm_io` for reads or writes. `complete_io` converts read jobs into write jobs after successful reads, records read/write errors, and either continues or completes depending on `DM_KCOPYD_IGNORE_ERROR`. Split jobs use `segment_complete` to atomically claim the next source range and dispatch replacement subjobs until all work is complete. Zeroing calls `dm_kcopyd_copy` with no source and uses `REQ_OP_WRITE_ZEROES` when all destinations support it, otherwise writes from a shared zero page list.

### State And Persistence Behavior
There is no persistent state. Runtime state lives in each client: reserved/free pages, pending job lists, throttle accounting, outstanding job count, split progress, and callback queues. `dm_kcopyd_client_destroy` waits until `nr_jobs` reaches zero before asserting all job lists are empty and releasing resources.

### Dependencies And Integration Points
This file depends on `linux/dm-kcopyd.h`, `linux/dm-io.h`, block device zoned/write-zeroes helpers, mempools, workqueues, page allocation, mutexes, spinlocks, and Device Mapper core module-parameter helpers. It builds on `dm_io` for the actual block I/O and is typically consumed by higher-level DM targets such as mirrors, snapshots, or thin provisioning.

### Risks And Edge Cases
The most delicate behavior is split-job accounting: the master job is freed only after all subjobs finish, while callbacks are forced onto the kcopyd workqueue to avoid caller-visible completion concurrency. Reserved pages protect against deadlocks, but page pressure still stalls work by requeueing page jobs. Sequential write mode for zoned devices serializes writes through `write_offset`; ignoring errors is disabled because skipping a failed sequential write would corrupt ordering. Throttle accounting uses global spinlock-protected decaying jiffies counters and sleeps in bounded loops, so rate limiting is approximate.

### Test Signals
Tests should cover single and split copies, multi-destination writes, zeroing with and without hardware write-zeroes support, read and write error propagation, `DM_KCOPYD_IGNORE_ERROR`, zoned-device sequential write ordering, client destruction while work is outstanding, low-memory reserved-page fallback, throttled clients, prepared callbacks, and `dm_kcopyd_client_flush` draining work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-kcopyd.c -->
