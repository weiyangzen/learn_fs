# Research: subset-b-000924

Grouped research for block-layer source files under `sources/distributed-fs/ceph-client/block/`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-core.c -->
# sources/distributed-fs/ceph-client/block/blk-core.c

## Purpose
`blk-core.c` is the central block-layer submission, queue lifetime, queue entry, plugging, polling, and accounting implementation. It is the path upper layers use through `submit_bio()` and the path stacking drivers use through `submit_bio_noacct()`. It also initializes global block infrastructure such as `kblockd`, request queue cache allocation, debugfs, operation/status string helpers, and block tracepoints.

## Important APIs, Types, and Functions
Important exported APIs include `blk_queue_flag_set()`, `blk_queue_flag_clear()`, `blk_op_str()`, `errno_to_blk_status()`, `blk_status_to_errno()`, `blk_status_to_str()`, `blk_sync_queue()`, `blk_set_pm_only()`, `blk_clear_pm_only()`, `blk_put_queue()`, `blk_get_queue()`, `submit_bio_noacct()`, `submit_bio()`, `bio_poll()`, `iocb_bio_iopoll()`, `bdev_start_io_acct()`, `bio_start_io_acct()`, `bdev_end_io_acct()`, `bio_end_io_acct_remapped()`, `blk_lld_busy()`, `kblockd_schedule_work()`, `kblockd_mod_delayed_work_on()`, `blk_start_plug()`, `blk_check_plugged()`, `blk_finish_plug()`, and `blk_io_schedule()`. Internal helpers validate read-only writes, end-of-device access, partitions, zone append constraints, atomic write sizing, queue entry, and recursive submission ordering.

## Control Flow
The normal caller path is `submit_bio()` -> `bio_set_ioprio()` -> `submit_bio_noacct()`. `submit_bio_noacct()` validates NOWAIT support, encryption support, fault injection, read-only writes, end-of-device access, partition remapping, flush/FUA reduction, operation capability, zoned constraints, discard/secure erase/write-zeroes support, and atomic write sizes. If throttling does not consume the bio, it calls `submit_bio_noacct_nocheck()`.

`submit_bio_noacct_nocheck()` traces enqueue, starts blk-cgroup accounting, and uses `current->bio_list` to avoid recursive stack growth from stacked devices. It dispatches to `__submit_bio_noacct_mq()` for mq-only queues or `__submit_bio_noacct()` for queues with a driver `submit_bio` method. `__submit_bio()` wraps each dispatch in a plug, enters the queue when needed, rejects unsupported polled bios, calls either `blk_mq_submit_bio()` or `disk->fops->submit_bio()`, then exits the queue.

Queue lifetime is managed by refcounts, `q_usage_counter`, freeze/death checks, and RCU freeing. `blk_queue_enter()` and `__bio_queue_enter()` wait on `mq_freeze_wq` unless NOWAIT is requested or the queue/disk is dying.

## State and Persistence
State is in `struct request_queue`, `struct block_device`, `struct bio`, per-task `current->bio_list` and `current->plug`, partition statistics, queue flags, queue refcounts, and global `blk_debugfs_root`/`kblockd_workqueue`. There is no persistent on-disk state; durability semantics are enforced by request flags such as `REQ_PREFLUSH` and `REQ_FUA`, and by queue feature checks.

## Dependencies and Integration Points
This file integrates with blk-mq, blk-cgroup throttling, partition stats, runtime PM, inline encryption, zoned block devices, fault injection, BPF/block tracepoints, debugfs, request queue freeze/quiesce, and stacked block drivers. It calls into device-specific `gendisk` file operations and request queue operations while enforcing common block-layer policy.

## Risks
Critical risks are ordering and lifetime bugs around queue freeze/death, recursive bio submission, `current->bio_list`, queue refcounting, and bio completion on errors. Capability checks must reject unsupported operations before drivers see them. Encryption support checks must remain synchronized with blk-crypto capability semantics. Partition remap and EOD checks are safety-critical because silent sector misaddressing would corrupt data. Plug flushing must avoid deadlocks during schedule/reclaim by flushing callbacks, mq lists, and cached requests.

## Test Signals
Useful signals include block tracepoints (`block_bio_queue`, remap, completion), fault-injection via `fail_make_request`, NOWAIT error paths, zoned append boundary tests, partition remap tests, read-only write warnings, flush/FUA feature matrix tests, polled I/O support tests, cgroup throttling interaction, and queue freeze/removal race tests. Unit-level assertions are mostly `WARN_ON_ONCE()`, `BUG_ON()`, lockdep maps, and compile-time `BUILD_BUG_ON()` checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-crypto-fallback.c -->
# sources/distributed-fs/ceph-client/block/blk-crypto-fallback.c

## Purpose
`blk-crypto-fallback.c` implements software crypto API fallback for blk-crypto when a block device does not natively support a raw-key inline-encryption configuration. It makes encrypted I/O appear like normal bios below the fallback boundary: write bios are encrypted into bounce-page bios before submission, and read bios are decrypted in place after completion.

## Important APIs, Types, and Functions
The exported/internal entry points are `blk_crypto_fallback_bio_prep()`, `blk_crypto_fallback_start_using_mode()`, and `blk_crypto_fallback_evict_key()`. `struct bio_fallback_crypt_ctx` stores a copy of the crypto context, the original iterator, and either read-decrypt work metadata or saved end_io/private fields. The fallback device is modeled as a `struct blk_crypto_profile` with `blk_crypto_fallback_ll_ops`, `blk_crypto_num_keyslots`, and per-slot `crypto_sync_skcipher` transforms.

Key helpers include `blk_crypto_fallback_init()`, `blk_crypto_fallback_keyslot_program()`, `blk_crypto_fallback_evict_keyslot()`, `blk_crypto_alloc_enc_bio()`, `__blk_crypto_fallback_encrypt_bio()`, `blk_crypto_fallback_encrypt_bio()`, `__blk_crypto_fallback_decrypt_bio()`, `blk_crypto_fallback_decrypt_endio()`, and `blk_crypto_dun_to_iv()`.

## Control Flow
Upper layers are expected to call `blk_crypto_start_using_key()`, which eventually calls `blk_crypto_fallback_start_using_mode()` for unsupported raw-key hardware configurations. That routine lazily initializes fallback global state, preallocates transforms for every fallback keyslot for the requested mode, and publishes readiness with release/acquire ordering through `tfms_inited[]`.

At submission time, `blk_crypto_fallback_bio_prep()` validates mode initialization and profile support. For writes, it obtains a fallback keyslot, encrypts each data unit from source pages into allocated bounce pages, builds one or more encrypted bios, and submits those bios. Completion frees bounce pages, propagates status to the source bio, and completes the original bio after all encrypted child bios finish. For reads, it saves the caller's `bi_private` and `bi_end_io`, stores a fallback context in the bio, clears the normal crypto context, and installs `blk_crypto_fallback_decrypt_endio()`. On successful read completion, that end_io queues work on `blk_crypto_wq`; the work item obtains a keyslot, decrypts the original submission range in place, frees the fallback context, sets status, and completes the restored bio.

## State and Persistence
State is global and in-memory only: transform arrays, fallback keyslots, fallback profile, bounce page mempool, fallback context mempool, encryption bioset, high-priority workqueue, random `blank_key`, and mode initialization flags. Per-bio state captures the crypt context and original iterator so decrypt/encrypt covers the submission range even if later splitting changes `bi_iter`.

## Dependencies and Integration Points
This file depends on the Linux crypto skcipher API, mempools, biosets, blk-cgroup bio association cloning, blk-crypto keyslot management, and the block bio submission/completion model. It integrates with `blk-crypto.c` as the fallback called by `__blk_crypto_submit_bio()`.

## Risks
The main risks are deadlocks from allocating transforms or memory in I/O paths, incorrect DUN advancement, alignment errors against data-unit size, completion accounting for multiple encrypted child bios, use-after-free in saved end_io/private restoration, and leaking sensitive key material. The design mitigates these with preallocation, mempools, keyslot profile reuse, explicit zero/blank-key eviction, and queueing decrypt work out of atomic completion context.

## Test Signals
Tests should cover raw-key fallback enablement, missing crypto algorithm returning `-ENOPKG`, write bounce bio splitting beyond `BIO_MAX_VECS`, read decrypt after bio splitting, unaligned bio rejection, child bio error propagation, key eviction, mode readiness races, and memory-pressure scenarios that exercise mempools without direct reclaim deadlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-crypto-fallback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-crypto-internal.h -->
# sources/distributed-fs/ceph-client/block/blk-crypto-internal.h

## Purpose
`blk-crypto-internal.h` is the private block-layer header that connects blk-crypto core, keyslot profile management, sysfs, request preparation, fallback support, and request/bio merge logic. It supplies conditional inline stubs when `CONFIG_BLK_INLINE_ENCRYPTION` or fallback support is disabled.

## Important APIs, Types, and Functions
The central private type is `struct blk_crypto_mode`, which records the sysfs name, crypto API cipher string, raw key size, security strength, and IV size for each encryption mode. The header declares `blk_crypto_modes[]`, `bio_crypt_dun_increment()`, `bio_crypt_rq_ctx_compatible()`, `bio_crypt_ctx_mergeable()`, `blk_crypto_get_keyslot()`, `blk_crypto_put_keyslot()`, `__blk_crypto_evict_key()`, `__blk_crypto_cfg_supported()`, `blk_crypto_ioctl()`, request keyslot functions, bio crypt context advance/free functions, and fallback functions.

Inline helpers include merge checks (`bio_crypt_ctx_back_mergeable()`, `bio_crypt_ctx_front_mergeable()`, `bio_crypt_ctx_merge_rq()`), request defaults (`blk_crypto_rq_set_defaults()`), request state predicates, `blk_crypto_supported()`, `bio_crypt_advance()`, `bio_crypt_free_ctx()`, `bio_crypt_do_front_merge()`, `blk_crypto_rq_get_keyslot()`, `blk_crypto_rq_put_keyslot()`, `blk_crypto_free_request()`, and `blk_crypto_rq_bio_prep()`.

## Control Flow
Request construction code uses the inlines to copy bio crypto context into requests, get or release hardware keyslots only when the request is encrypted, and maintain DUN continuity during front merges. Merge code uses the compatibility helpers to reject merging encrypted bios or requests with incompatible keys or non-contiguous data unit numbers. Submission code calls `blk_crypto_supported()` to require native support in `submit_bio_noacct()` and calls fallback preparation through the exported fallback hook when configured.

## State and Persistence
The header owns no runtime storage, but it defines the expectations for `request->crypt_ctx`, `request->crypt_keyslot`, `bio->bi_crypt_context`, and `blk_crypto_key` mode metadata. Its disabled-configuration stubs are significant state behavior: they make non-encryption builds compile while returning false support, no-op cleanup, and `-ENOTTY` for crypto ioctls.

## Dependencies and Integration Points
It includes `linux/bio.h` and `linux/blk-mq.h` and is included by crypto core, sysfs, profile, fallback, and request preparation paths. It bridges public blk-crypto APIs, private block request internals, and compile-time feature flags.

## Risks
Because these are hot-path inline helpers, a semantic mismatch between enabled and disabled stubs can create subtle bugs. Mergeability depends on DUN continuity and key pointer identity; relaxing it incorrectly would corrupt encrypted data. Request cleanup assumes keyslots are put before crypt contexts are freed. Stubs must preserve existing non-encryption behavior and reject ioctls/support queries predictably.

## Test Signals
Relevant tests are build coverage for all combinations of inline encryption and fallback config, encrypted request merge tests, front/back merge DUN tests, disabled-config ioctl behavior, keyslot get/put balancing, and request cleanup assertions that `crypt_keyslot` is not leaked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-crypto-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-crypto-profile.c -->
# sources/distributed-fs/ceph-client/block/blk-crypto-profile.c

## Purpose
`blk-crypto-profile.c` implements generic inline-encryption device profiles and keyslot management. Storage drivers expose capabilities and hardware operations through `struct blk_crypto_profile`; the block layer uses this file to allocate, program, reuse, evict, and reprogram keyslots independent of device-specific details.

## Important APIs, Types, and Functions
The key private type is `struct blk_crypto_keyslot`, containing a reference count, idle LRU node, hash node, key pointer, and backpointer to the profile. Public APIs include `blk_crypto_profile_init()`, `devm_blk_crypto_profile_init()`, `blk_crypto_keyslot_index()`, `blk_crypto_get_keyslot()`, `blk_crypto_put_keyslot()`, `__blk_crypto_cfg_supported()`, `__blk_crypto_evict_key()`, `blk_crypto_reprogram_all_keys()`, `blk_crypto_profile_destroy()`, `blk_crypto_register()`, hardware-wrapped-key helpers (`blk_crypto_derive_sw_secret()`, `blk_crypto_import_key()`, `blk_crypto_generate_key()`, `blk_crypto_prepare_key()`), and capability helpers (`blk_crypto_intersect_capabilities()`, `blk_crypto_has_capabilities()`, `blk_crypto_update_capabilities()`).

## Control Flow
Drivers initialize a profile, fill low-level operations and capability bitmaps, and register it on a queue. If keyslots exist, initialization builds an idle slot list and hash table. For I/O, `blk_crypto_get_keyslot()` first tries a read-locked lookup for an already programmed key. If not found, it enters hardware access with runtime PM and write lock, waits for an idle slot if none are free, programs the key with `ll_ops.keyslot_program`, updates the key hash, sets refs to one, and removes the slot from the idle LRU. Completion calls `blk_crypto_put_keyslot()`, which returns a slot to the idle list and wakes waiters when refs drop to zero.

Eviction removes a key from profile management and calls driver `keyslot_evict` when needed. Hardware reset recovery calls `blk_crypto_reprogram_all_keys()` to reprogram every slot that still has a key pointer. Hardware-wrapped-key ioctls in `blk-crypto.c` call this file's import/generate/prepare/derive helpers, each protected by the same hardware enter/exit sequence.

## State and Persistence
Persistent runtime state is in `struct blk_crypto_profile`: lockdep key, rwsem, optional device for runtime PM, slots array, idle list/spinlock/waitqueue, key hash table, capability bitmaps, max DUN size, key type support, and low-level ops. Key identity is pointer-based; the block layer expects callers not to free keys until eviction and I/O quiescence rules are satisfied.

## Dependencies and Integration Points
This file integrates with request queues, runtime PM, blk-integrity, low-level storage drivers, device-managed resources, hardware-wrapped-key ioctls, and layered-device capability propagation. `blk_crypto_register()` refuses hardware inline encryption when queue integrity is enabled.

## Risks
Risk concentrates around key lifetime, slot refcounting, hardware programming while the device is suspended, and lock ordering between runtime PM and `profile->lock`. The code deliberately resumes the device before taking the profile write lock because resume paths can re-enter key reprogramming. Eviction unlinks keys even on hardware errors because callers may free keys immediately; this avoids stale key pointers but requires warnings to catch driver failures.

## Test Signals
Tests should exercise no-slot profiles, single-slot hash sizing, slot reuse, idle-slot waiting, concurrent get/put/evict, runtime PM reprogramming, wrapped-key unsupported paths, integrity conflict disabling, layered capability intersection/update, and reset recovery through `blk_crypto_reprogram_all_keys()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-crypto-profile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-crypto-sysfs.c -->
# sources/distributed-fs/ceph-client/block/blk-crypto-sysfs.c

## Purpose
`blk-crypto-sysfs.c` exposes inline-encryption capabilities through `/sys/block/$disk/queue/crypto/`. It creates a `crypto` kobject under a disk queue and publishes supported key types, DUN width, number of keyslots, and per-mode data-unit-size masks.

## Important APIs, Types, and Functions
`struct blk_crypto_kobj` embeds a kobject and points to the queue's `blk_crypto_profile`. `struct blk_crypto_attr` wraps a sysfs attribute and profile-aware show callback. Exported functions are `blk_crypto_sysfs_register()` and `blk_crypto_sysfs_unregister()`. Static show callbacks include `hw_wrapped_keys_show()`, `raw_keys_show()`, `max_dun_bits_show()`, `num_keyslots_show()`, and `blk_crypto_mode_show()`.

## Control Flow
At boot, `blk_crypto_sysfs_init()` initializes one attribute per encryption mode from `blk_crypto_modes[]`, skipping mode zero because `BLK_ENCRYPTION_MODE_INVALID` is expected to be zero. When a disk queue is registered, `blk_crypto_sysfs_register()` checks `q->crypto_profile`; if present, it allocates a wrapper object, points it at the profile, and calls `kobject_init_and_add()` under the queue kobject as `crypto`. Attribute visibility filters hide raw or hardware-wrapped key files if the key type is unsupported and hide mode files if the corresponding mode mask is zero. Unregistering simply puts the stored kobject.

## State and Persistence
The sysfs kobject is transient queue-registration state stored in `q->crypto_kobject`. Attribute values are read directly from the profile and are not persisted. Mode attributes are initialized once at subsystem init into static arrays.

## Dependencies and Integration Points
This file depends on `blk-crypto-internal.h`, `blk_crypto_modes[]`, queue sysfs registration, and profile capability fields. Userspace filesystems and tooling use this tree to decide whether direct inline encryption is available and what configurations are legal.

## Risks
Risks include stale profile pointers if unregister ordering is wrong, exposing unsupported capabilities due to visibility errors, and mode array indexing bugs. The use of `kobject_put()` on registration failure and unregister is essential because the release handler frees the wrapper object.

## Test Signals
Tests should verify sysfs presence only for queues with crypto profiles, visibility of `raw_keys` and `hw_wrapped_keys`, `max_dun_bits` calculation, `num_keyslots`, mode file names matching `blk_crypto_modes[]`, absence of invalid mode zero, and clean register/unregister under disk teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-crypto-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-crypto.c -->
# sources/distributed-fs/ceph-client/block/blk-crypto.c

## Purpose
`blk-crypto.c` implements the core blk-crypto bio context, encryption mode table, request crypto preparation, key validation, capability checks, key lifecycle operations, fallback selection, and crypto ioctls. It is the central glue between filesystem encryption users, request construction, device crypto profiles, and software fallback.

## Important APIs, Types, and Functions
Important functions include `bio_crypt_set_ctx()`, `__bio_crypt_free_ctx()`, `__bio_crypt_clone()`, `bio_crypt_dun_increment()`, `__bio_crypt_advance()`, `bio_crypt_dun_is_contiguous()`, `bio_crypt_rq_ctx_compatible()`, `bio_crypt_ctx_mergeable()`, `__blk_crypto_rq_get_keyslot()`, `__blk_crypto_rq_put_keyslot()`, `__blk_crypto_free_request()`, `__blk_crypto_submit_bio()`, `__blk_crypto_rq_bio_prep()`, `blk_crypto_init_key()`, `blk_crypto_config_supported_natively()`, `blk_crypto_config_supported()`, `blk_crypto_start_using_key()`, `blk_crypto_evict_key()`, and `blk_crypto_ioctl()`.

## Control Flow
Subsystem init creates a mempool-backed `bio_crypt_ctx` cache and validates every mode's key size, security strength, and IV size. Upper layers initialize keys with `blk_crypto_init_key()`, attach key and DUN to bios with `bio_crypt_set_ctx()`, and call `blk_crypto_start_using_key()` before data-path use when fallback might be needed. Submission checks call `__blk_crypto_submit_bio()` for encrypted bios. If the queue supports the config natively, the bio continues. If not, raw-key bios can be consumed by fallback; wrapped-key bios or disabled fallback produce errors.

Request setup copies the bio crypt context into `rq->crypt_ctx`; dispatch gets a profile keyslot through `blk_crypto_get_keyslot()`, and request cleanup releases keyslot/context. Mergeability uses key pointer equality and DUN continuity to avoid combining incompatible encrypted regions.

The ioctl path requires a queue crypto profile and supports importing raw keys into long-term wrapped keys, generating wrapped keys, and preparing long-term wrapped keys into ephemeral keys. It validates reserved fields and buffer sizes, copies user buffers, calls profile operations, copies results back, and zeroes temporary key buffers.

## State and Persistence
State is per-bio `bio_crypt_ctx`, per-request copied crypt context and keyslot pointer, the static `blk_crypto_modes[]` table, and the crypt context mempool. Keys are caller-owned; this file stores pointers and requires callers to evict before freeing. There is no disk persistence, but ioctl operations produce hardware-wrapped key material for userspace.

## Dependencies and Integration Points
Dependencies include blk-crypto profiles, fallback, block device queues, mempools, usercopy, module parameters, and fscrypt-style upper layers. `submit_bio_noacct()` and blk-mq request code rely on these helpers for validation and request preparation.

## Risks
Risks include DUN arithmetic overflow, incorrect data-unit-size shifts, accepting malformed key sizes or DUN widths, failing to pre-start fallback transforms, leaking temporary key material, and key pointer lifetime violations. Mempool allocation assumptions are explicit: callers using `bio_crypt_set_ctx()` must pass reclaim-capable GFP flags.

## Test Signals
Tests should cover mode table validation, key initialization for raw and wrapped keys, invalid key sizes/DUN sizes/data unit sizes, DUN increment and contiguity, clone/free paths, native vs fallback support decisions, fallback-disabled failures, request keyslot get/put balance, ioctls with reserved fields and too-small output buffers, and temporary key zeroing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-flush.c -->
# sources/distributed-fs/ceph-client/block/blk-flush.c

## Purpose
`blk-flush.c` implements the block-layer state machine that decomposes `REQ_PREFLUSH` and `REQ_FUA` writes into preflush, data, and postflush steps according to queue write-cache and FUA capabilities. It merges compatible flush work and serializes actual flush commands so durability ordering is preserved without issuing redundant cache flushes.

## Important APIs, Types, and Functions
Important functions include `blk_insert_flush()`, `blkdev_issue_flush()`, `blk_alloc_flush_queue()`, `blk_free_flush_queue()`, `blk_mq_hctx_set_fq_lock_class()`, `is_flush_rq()`, `flush_end_io()`, `mq_flush_data_end_io()`, `blk_flush_complete_seq()`, `blk_kick_flush()`, and `blk_rq_init_flush()`. The sequence bits are `REQ_FSEQ_PREFLUSH`, `REQ_FSEQ_DATA`, `REQ_FSEQ_POSTFLUSH`, and `REQ_FSEQ_DONE`.

## Control Flow
`blk_insert_flush()` inspects a request's data length, `REQ_PREFLUSH`, `REQ_FUA`, queue write-cache flag, and FUA support. If nothing is needed, empty flushes complete immediately or data requests proceed normally. If data plus postflush is needed, the request's end_io is replaced so data completion re-enters the flush state machine. Other policies queue the request through `blk_flush_complete_seq()`.

Flush queues are double-buffered by `flush_pending_idx` and `flush_running_idx`. Requests that need pre/post flush are placed on the pending list. `blk_kick_flush()` issues one synthetic `REQ_OP_FLUSH | REQ_PREFLUSH` request when no flush is already running, unless data requests are in flight and the pending timeout has not expired. The synthetic flush borrows tags from the first queued request and is placed on `q->flush_list`. `flush_end_io()` accounts the flush, restores tag state, flips the running buffer, and advances all waiting requests to their next sequence step. Data completion decrements `flush_data_in_flight` and continues the sequence.

## State and Persistence
State is in `struct blk_flush_queue`: two flush lists, pending/running indices, a synthetic flush request, `mq_flush_lock`, `flush_data_in_flight`, pending timestamp, and aggregated flush status. Per-request state is `rq->flush.seq`, saved end_io, `RQF_FLUSH_SEQ`, and temporary queue-list placement.

## Dependencies and Integration Points
This file integrates with blk-mq requeueing, request tags, schedulers/elevators, partition flush statistics, `submit_bio_wait()` through `blkdev_issue_flush()`, and queue limits/features. Drivers see either real data requests with adjusted flags or synthetic flush requests generated here.

## Risks
Risks include durability violations from incorrect sequence transitions, tag ownership mistakes, double completion of flush-sequenced requests, starvation when data traffic continuously delays postflushes, recursive lockdep false positives, and scheduler/no-scheduler tag differences. The code relies on one-bio flush/FUA requests and uses timeout-based kicking to avoid indefinite flush deferral.

## Test Signals
Tests should exercise every write-cache/FUA capability matrix, empty flush completion, data-only bypass, preflush+data+postflush ordering, error propagation from synthetic flush to waiting requests, pending timeout under continuous FUA data, scheduler and no-scheduler tag paths, request accounting for flush stats, and teardown of allocated flush queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-ia-ranges.c -->
# sources/distributed-fs/ceph-client/block/blk-ia-ranges.c

## Purpose
`blk-ia-ranges.c` manages independent access ranges for block devices. These ranges describe non-overlapping, capacity-covering LBA regions that can be accessed independently, and it exposes them through queue sysfs under `independent_access_ranges`.

## Important APIs, Types, and Functions
Public functions are `disk_alloc_independent_access_ranges()` and `disk_set_independent_access_ranges()`. Queue registration paths use `disk_register_independent_access_ranges()` and `disk_unregister_independent_access_ranges()`. Static helpers include sysfs show methods for `sector` and `nr_sectors`, `disk_find_ia_range()`, `disk_check_ia_ranges()`, and `disk_ia_ranges_changed()`.

## Control Flow
Drivers allocate a `struct blk_independent_access_ranges` sized for `nr_ia_ranges`, fill each range, and call `disk_set_independent_access_ranges()`. That function takes `q->sysfs_lock`, validates the proposed ranges, frees unchanged replacements, unregisters the old set, assigns the new set, and registers sysfs immediately if the queue is already registered.

Validation requires at least one range, no overlap, no holes, sorted coverage from sector zero, and total coverage equal to disk capacity. It sorts in place by repeatedly finding the range that starts at the expected sector and swapping it into position. Sysfs registration creates a parent `independent_access_ranges` kobject and numbered child kobjects, each exposing read-only `sector` and `nr_sectors`.

## State and Persistence
Runtime state hangs off `disk->ia_ranges`. Sysfs registration state is tracked by `iars->sysfs_registered` and kobjects embedded in the parent and each range. Range memory is freed only after kobject teardown is safe; individual range kobject release is intentionally a no-op because the parent allocation owns the flexible array.

## Dependencies and Integration Points
The file depends on `gendisk`, request queue sysfs locking, queue registration state, disk capacity, and kobject sysfs. It is driver-facing through exported allocation/set APIs and user-facing through queue sysfs.

## Risks
Risks include invalid device topology exposure, kobject lifetime mistakes, leaks on partial sysfs registration failure, and racing revalidation with queue sysfs. The validation rejects holes and capacity mismatch to prevent user space from relying on incomplete topology. Lockdep assertions enforce `q->sysfs_lock` for register/unregister.

## Test Signals
Tests should cover unsorted valid ranges, overlaps, holes, capacity mismatch, zero ranges, unchanged replacement freeing, setting NULL to clear, register/unregister before and after queue registration, partial child kobject failure unwinding, and sysfs values for each numbered range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-ia-ranges.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-integrity.c -->
# sources/distributed-fs/ceph-client/block/blk-integrity.c

## Purpose
`blk-integrity.c` implements block-layer data integrity metadata support. It counts integrity scatterlist segments, maps user-provided metadata to requests, reports logical block metadata capabilities, controls integrity verification/generation sysfs flags, and enforces merge compatibility for bios and requests carrying integrity payloads.

## Important APIs, Types, and Functions
Important functions are `blk_rq_count_integrity_sg()`, `blk_get_meta_cap()`, `blk_rq_integrity_map_user()`, `blk_integrity_merge_rq()`, `blk_integrity_merge_bio()`, `blk_integrity_profile_name()`, and the `blk_integrity_attr_group`. Sysfs callbacks expose `format`, `tag_size`, `protection_interval_bytes`, `read_verify`, `write_generate`, and `device_is_integrity_capable`.

## Control Flow
`blk_rq_count_integrity_sg()` walks a bio's integrity vectors and merges adjacent physical segments subject to queue mergeability and max segment size. `blk_rq_integrity_map_user()` creates an iov iterator from a user buffer, maps it into the request bio's integrity payload, computes segment count, and sets `REQ_INTEGRITY`.

`blk_get_meta_cap()` validates the extensible ioctl, reads the disk integrity profile, and fills logical block metadata capability fields: protection interval, metadata size, PI size/offset, opaque metadata layout, checksum type, app tag size, and ref tag size. Merge checks require both sides either have no integrity or both do, then compare payload flags, app tag when checked, max integrity segment limits, and gap constraints.

Sysfs write toggles invert user-facing `read_verify`/`write_generate` values into internal `BLK_INTEGRITY_NOVERIFY` and `BLK_INTEGRITY_NOGENERATE` flags through frozen queue limits updates.

## State and Persistence
State is in `queue->limits.integrity`, per-bio `bio_integrity_payload`, request `nr_integrity_segments`, and `REQ_INTEGRITY`. Sysfs changes update queue limits rather than writing persistent media state.

## Dependencies and Integration Points
This file integrates with T10 PI/extended DIF tuple definitions, block queue limits, request/bio merging, user ioctl copy helpers, bio integrity mapping, and queue sysfs. It also gates hardware inline encryption indirectly because `blk_crypto_register()` refuses integrity-capable queues.

## Risks
Risks include mismatched metadata and data segment merging, incorrect advertised capability layout, user pointer mapping failures, and unsafe flag changes without queue freezing. The inverted sysfs flags are easy to misread: writing `1` enables verification/generation by clearing the no-verify/no-generate bit.

## Test Signals
Tests should cover segment coalescing, max segment size/limit rejection, request and bio merge compatibility, app-tag mismatch, ref-tag capability reporting for CRC/IP/CRC64, ioctl extensible-size handling, user metadata mapping failure, sysfs flag toggles, and integrity plus inline-encryption exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-integrity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-ioc.c -->
# sources/distributed-fs/ceph-client/block/blk-ioc.c

## Purpose
`blk-ioc.c` manages per-task `io_context` objects and, when `CONFIG_BLK_ICQ` is enabled, per-queue `io_cq` associations used by I/O schedulers. It handles reference counting, task inheritance, ioprio storage, scheduler callback lifetime, and queue cleanup.

## Important APIs, Types, and Functions
Important functions include `put_io_context()`, `exit_io_context()`, `set_task_ioprio()`, `__copy_io()`, `ioc_lookup_icq()`, `ioc_find_get_icq()`, and `ioc_clear_queue()`. Internal helpers include `alloc_io_context()`, `get_io_context()`, `ioc_exit_icq()`, `ioc_destroy_icq()`, `ioc_release_fn()`, `ioc_delay_free()`, and `ioc_create_icq()`.

## Control Flow
An `io_context` is allocated lazily when ioprio is set, a task copies I/O state, or an ICQ is requested. `set_task_ioprio()` checks credentials and LSM policy, allocates if needed, handles races with task exit or another allocator, and updates `ioc->ioprio`. `__copy_io()` shares the parent's context for `CLONE_IO`, otherwise copies only valid ioprio into a new context.

With `CONFIG_BLK_ICQ`, schedulers request a queue-specific context through `ioc_find_get_icq()`. It ensures a current task context exists, looks up an existing ICQ via RCU hint or radix tree, and creates one under both queue and ioc locks if missing. Queue clearing walks `q->icq_list` and destroys every association. Final ioc release is delayed to `system_power_efficient_wq` if ICQs remain, because destroying them requires queue/ioc double locking that might conflict with current lock context.

## State and Persistence
State is per-task `task->io_context`, `io_context.refcount`, `active_ref`, `ioprio`, optional radix tree/list of ICQs, RCU hint pointer, and per-queue `q->icq_list`. ICQs carry scheduler-specific storage allocated from the elevator's cache. No persistent state exists beyond task lifetime.

## Dependencies and Integration Points
This file integrates with task credentials, LSM `security_task_setioprio()`, sched/task exit, blk-mq schedulers, elevator ICQ callbacks, radix trees, RCU, queue locks, and slab cache initialization.

## Risks
Risks are lifetime and lock-order bugs between task exit, queue teardown, scheduler ICQ callbacks, and RCU lookup. The release worker performs careful double-locking and RCU protection to avoid freeing queues or ICQs while resolving lock order. Missing `put_io_context()` after `ioc_find_get_icq()` users would leak contexts.

## Test Signals
Tests should cover ioprio permission denial, LSM denial, lazy allocation races, `CLONE_IO` sharing, non-shared ioprio copy, ICQ lookup hint hits/misses, duplicate ICQ creation races, queue clearing during task exit, delayed release path, and builds without `CONFIG_BLK_ICQ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-ioc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-iocost.c -->
# sources/distributed-fs/ceph-client/block/blk-iocost.c

## Purpose
`blk-iocost.c` implements the cgroup v2 IO cost controller. It estimates I/O cost using a linear cost model, charges cgroups in device virtual time, throttles issuers that outrun their hierarchical share, dynamically adjusts the device virtual rate based on latency/rq-wait signals, and donates unused weight to maintain work conservation.

## Important APIs, Types, and Functions
The main per-device state is `struct ioc`, embedded as `rq_qos` and holding parameters, margins, vrate, timer, active cgroups, stats, autop profile state, and hweight generation. Per-device-cgroup state is `struct ioc_gq`, holding weights, inuse/active state, vtime/done_vtime, debt/delay, waitqueue, hweight caches, stats, and ancestor pointers. Per-cgroup state is `struct ioc_cgrp`, mostly the default weight.

Important functions include parameter setup (`ioc_refresh_period_us()`, `ioc_refresh_params_disk()`, `ioc_refresh_lcoefs()`), hweight propagation (`__propagate_weights()`, `current_hweight()`, `weight_updated()`), activation (`iocg_activate()`), throttling/debt (`ioc_rqos_throttle()`, `iocg_incur_debt()`, `iocg_pay_debt()`, `iocg_kick_waitq()`), donation (`hweight_after_donation()`, `transfer_surpluses()`), periodic control (`ioc_timer_fn()`, `ioc_check_iocgs()`, `ioc_adjust_base_vrate()`), cost calculation (`calc_vtime_cost_builtin()`), rq-qos hooks, and cgroup file handlers for `io.weight`, `io.cost.qos`, and `io.cost.model`.

## Control Flow
The controller is lazily initialized when root cgroup cost files are written for a queue. `blk_iocost_init()` allocates `struct ioc`, per-cpu stats, initializes timer/vtime/autop parameters, adds rq-qos hooks, and activates the blkcg policy. `io.cost.qos` enables/disables the controller, toggles request allocation-time accounting, quiesces the queue while changing settings, and disables default writeback throttling while iocost is enabled. `io.cost.model` freezes and quiesces the queue while changing linear model coefficients.

On bio issue, `ioc_rqos_throttle()` bypasses disabled/root/non-cost bios, calculates absolute cost from operation type, size, and sequential cursor, activates the leaf iocg, converts absolute cost to cgroup cost using current hweight, and either commits immediately or blocks on the iocg waitqueue until enough vtime budget exists. Bios that cannot safely block, such as root-issued or fatal-signal contexts, are issued as debt and later paid down from future budget while cgroup delay is applied. Merge hooks account extra cost for merged bios, often as debt if immediate budget is unavailable. Completion hooks advance `done_vtime` and collect latency/rq-wait signals.

The periodic timer updates active iocgs, wakes oversleeping waiters, deactivates idle groups, flushes stats up the hierarchy, detects surpluses and shortages, transfers donated inuse weight, adjusts vrate up/down based on request wait and latency misses, refreshes autop parameters, forgives old debt when the device is underutilized, and either starts the next period or returns to idle.

## State and Persistence
Runtime state spans rq-qos device objects, blkcg policy data, per-cpu counters, timers, hrtimers, waitqueues, active lists, cgroup file settings, and queue flags. There is no on-disk persistence; configuration lives in cgroupfs and runtime kernel objects. The controller maintains virtual-time accounting in microsecond-based wall time and high-resolution virtual time.

## Dependencies and Integration Points
This file integrates with blk-rq-qos, blkcg policy registration, cgroup v2 `io.*` files, blk-stat latency accounting, blk-wbt, blk-mq freeze/quiesce, request allocation timestamps, block tracepoints, and bio cgroup association. It depends on hierarchical cgroup topology through ancestor arrays and blkcg_gq parents.

## Risks
The high-risk areas are arithmetic overflow/rounding in hweight and vtime math, races between activation/deactivation and waitqueue/debt handling, timer lifecycle during policy teardown, cgroup removal while debt/delay exists, queue freeze/quiesce ordering during config writes, and fairness regressions from donation or vrate feedback. The code deliberately separates absolute cost from hweight-relative cost for debt so future hweight changes are accounted correctly.

## Test Signals
Useful tests include enabling/disabling on mq and non-mq queues, `io.weight` default and per-device parsing, `io.cost.qos` and `io.cost.model` invalid-token handling, latency/rq-wait vrate adjustment, multiple cgroup hierarchy fairness, debt path for root/fatal-signal bios, waitqueue wake timing, merge charging, idle deactivation, donation under underutilized groups, queue-depth changes, policy teardown with active timers, and tracepoint/`io.stat` counters for usage/wait/indebt/indelay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-iocost.c -->
