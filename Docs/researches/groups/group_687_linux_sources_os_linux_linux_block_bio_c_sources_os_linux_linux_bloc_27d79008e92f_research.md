# Group Research: group_687_linux_sources_os_linux_linux_block_bio_c_sources_os_linux_linux_bloc_27d79008e92f

Scope: subset A, source tree `sources/os/linux/linux`, focused on Linux block-layer bio, blkcg, core submit, inline crypto, and flush sequencing files. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/bio.c -->
# File Research: sources/os/linux/linux/block/bio.c

## Scope

This file implements core Linux `struct bio` lifecycle and data-vector helpers: bio/bvec allocation, cloning, chaining, splitting, trimming, iterator-to-bio page extraction, bounce buffering, synchronous waits, completion, page dirtying, and global bioset initialization.

## Core APIs and Entry Points

- Bio initialization/reuse:
  - `bio_init()`, `bio_reset()`, `bio_reuse()`, `bio_uninit()`.
- Allocation and release:
  - `bio_alloc_bioset()`, `bio_kmalloc()`, `bio_put()`, internal `bio_free()`.
  - `bioset_init()`, `bioset_exit()`, `biovec_init_pool()`.
- Chaining and synchronous submission helpers:
  - `bio_chain()`, `bio_chain_and_submit()`, `blk_next_bio()`.
  - `bio_await()`, `submit_bio_wait()`, `bio_submit_or_kill()`, `bdev_rw_virt()`.
- Payload construction:
  - `bio_add_page()`, `__bio_add_page()`, `bio_add_folio()`, `bio_add_folio_nofail()`.
  - `bio_add_virt_nofail()`, `bio_add_vmalloc_chunk()`, `bio_add_vmalloc()`.
  - `bio_iov_iter_get_pages()`, `bio_iov_iter_bounce()`, `bio_iov_iter_unbounce()`.
- Data movement and completion:
  - `__bio_advance()`, `bio_copy_data_iter()`, `bio_copy_data()`, `bio_free_pages()`.
  - `bio_set_pages_dirty()`, `bio_check_pages_dirty()`, `bio_endio()`.
  - `bio_split()`, `bio_trim()`, `guard_bio_eod()`.

## Major State

- `fs_bio_set` is the default global bio pool for general block I/O.
- `bvec_slabs[]` maps requested vector counts to shared `bio_vec` slab caches.
- `bio_slabs` xarray and `bio_slab_lock` share `bio` slabs keyed by combined front pad, `struct bio`, and back pad size.
- `struct bio_alloc_cache` provides per-cpu cached inline-vector bios plus a hardirq side list.
- Biosets may own:
  - `bio_pool` and `bvec_pool` mempools,
  - optional rescuer workqueue/list for avoiding nested allocation deadlocks,
  - optional per-cpu allocation cache.
- Dirty-page deferral uses `bio_dirty_list`, `bio_dirty_lock`, and `bio_dirty_work`.

## Control Flow

- `bio_alloc_bioset()` first tries a non-blocking slab or per-cpu cache allocation. If direct reclaim is allowed and the fast path fails, it punts same-bioset bios from `current->bio_list` to the bioset rescuer and falls back to mempools.
- Inline-vector bios use storage after `struct bio`; larger vector arrays come from `bvec_slabs[]` or the bioset bvec mempool.
- `bio_put()` decrements `__bi_cnt` only when `BIO_REFFED` is set, then either returns an inline-vector bio to the per-cpu cache or fully frees it.
- `bio_chain()` increments the parent remaining count and uses a sentinel `bio_chain_endio`; `bio_endio()` handles chained bios iteratively to avoid recursion.
- `bio_iov_iter_get_pages()` either aliases an existing bvec iterator as a cloned bio or extracts/pins pages into the bio, then aligns total length down if required.
- Bounce-buffer helpers allocate folios, copy write data into them, or store read bounce storage at `bi_io_vec[0]`; unbounce copies read data back and releases pins/folios.
- Direct-I/O read dirtying is deferred if pages became clean before completion, because marking dirty may need process context.
- `init_bio()` creates biovec slabs, registers CPU hotplug cleanup, and initializes `fs_bio_set`.

## Dependencies

- Block APIs: `submit_bio()`, `submit_bio_noacct()`, `bio_advance_iter()`, `bio_integrity_*`, `bio_crypt_*`, `bio_associate_blkg()`, `rq_qos_done_bio()`, zone completion helpers.
- Memory APIs: mempools, slab caches, folios, page pin/unpin, vmalloc mapping helpers, kmap-local bvec access, kmemleak.
- Concurrency: per-cpu caches, CPU hotplug callbacks, spinlocks, atomics, workqueues.

## Risks and Invariants

- Bios allocated with `bio_init()` outside a bioset must be paired with `bio_uninit()` by the owner.
- Callers must not allocate multiple bios from the same mempool under recursive `submit_bio_noacct()` unless previous bios are submitted or a rescuer is available.
- `bio_reuse()` refuses cloned, integrity, and crypto-context bios.
- Bio vector tables are intentionally immutable in several truncation/split paths; callers must use iterators rather than modifying bvec layout.
- `bio_split()` forbids zone append and atomic writes.
- Per-cpu cached bios are `SLAB_TYPESAFE_BY_RCU`, so poll paths must tolerate seeing freshly reallocated bios.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-cgroup-fc-appid.c -->
# File Research: sources/os/linux/linux/block/blk-cgroup-fc-appid.c

## Scope

This small file provides Fibre Channel application-id storage and lookup on block cgroups when `CONFIG_BLK_CGROUP_FC_APPID` is enabled.

## Core APIs

- `blkcg_set_fc_appid()` sets `blkcg->fc_app_id` for a cgroup identified by numeric cgroup id.
- `blkcg_get_fc_appid()` returns the application id associated with a bio’s `bi_blkg`, or `NULL` if none exists.

## Control Flow

- `blkcg_set_fc_appid()` validates `app_id_len <= FC_APPID_LEN`, obtains the cgroup by id, obtains the io controller css with `cgroup_get_e_css()`, converts it to `struct blkcg`, and stores the string with `strscpy()`.
- `blkcg_get_fc_appid()` requires a bio blkcg association and a nonempty `fc_app_id`.

## Dependencies

- `blk-cgroup.h` for `struct blkcg`, `css_to_blkcg()`, and `io_cgrp_subsys`.
- Cgroup reference APIs: `cgroup_get_from_id()`, `cgroup_get_e_css()`, `css_put()`, `cgroup_put()`.

## Risks and Invariants

- Setting the app id is intentionally lockless. The comment accepts a small race where an I/O may observe no id or an older id.
- The length check rejects values larger than `FC_APPID_LEN`, but callers must still provide a sensible string buffer for `strscpy()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-cgroup-fc-appid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-cgroup-rwstat.c -->
# File Research: sources/os/linux/linux/block/blk-cgroup-rwstat.c

## Scope

This file implements legacy block-cgroup read/write stat helpers enabled by `CONFIG_BLK_CGROUP_RWSTAT`. The header explicitly marks them as legacy and not for new code.

## Core APIs

- `blkg_rwstat_init()` initializes `BLKG_RWSTAT_NR` percpu counters and zeroes auxiliary counters.
- `blkg_rwstat_exit()` destroys the percpu counters.
- `__blkg_prfill_rwstat()` prints a sampled rwstat for one device.
- `blkg_prfill_rwstat()` reads a rwstat at an offset inside policy data and prints it.
- `blkg_rwstat_recursive_sum()` walks a blkg subtree and sums local plus auxiliary counts.

## Control Flow

- Printing emits per-device `Read`, `Write`, `Sync`, `Async`, `Discard`, and `Total` lines.
- Recursive summing walks descendants with `blkg_for_each_descendant_pre()` under RCU while the caller holds the queue lock for stable online checks.
- If `pol` is non-NULL, `off` is relative to the blkg policy data; otherwise it is relative to `struct blkcg_gq`.

## Dependencies

- `blk-cgroup-rwstat.h` types and inline add/read/reset helpers.
- `blk-cgroup.h` traversal and policy-data helpers.
- `percpu_counter_*`, `atomic64_t`, `seq_file`.

## Risks and Invariants

- The caller of recursive summing must hold `blkg->q->queue_lock`.
- Auxiliary counters carry stats of dead children and are included in recursive totals but excluded from local `blkg_rwstat_read()`.
- Since these are legacy helpers, new policies should prefer the newer iostat/rstat path in `blk-cgroup.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-cgroup-rwstat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-cgroup-rwstat.h -->
# File Research: sources/os/linux/linux/block/blk-cgroup-rwstat.h

## Scope

This private header defines legacy rwstat data structures and inline helpers for block-cgroup policy stats.

## Major Types

- `enum blkg_rwstat_type` tracks `READ`, `WRITE`, `SYNC`, `ASYNC`, and `DISCARD`.
- `struct blkg_rwstat` contains one percpu counter and one auxiliary atomic counter per stat type.
- `struct blkg_rwstat_sample` is a fixed array snapshot of counts.

## Core Helpers

- `blkg_rwstat_add()` classifies an operation by read/write/discard and sync/async, then adds to the relevant counters using `BLKG_STAT_CPU_BATCH`.
- `blkg_rwstat_read()` snapshots percpu counters only.
- `blkg_rwstat_total()` returns read plus write local total.
- `blkg_rwstat_reset()` clears percpu and auxiliary counters.
- `blkg_rwstat_add_aux()` folds another rwstat’s local and auxiliary counts into this rwstat’s auxiliary counters.
- Non-inline functions declared here are implemented in `blk-cgroup-rwstat.c`.

## Dependencies

- `blk-cgroup.h` for `BLKG_STAT_CPU_BATCH`, blkg traversal, and policy data.
- Request operation helpers: `op_is_discard()`, `op_is_write()`, `op_is_sync()`.

## Risks and Invariants

- `blkg_rwstat_add()` assumes external synchronization appropriate to the policy.
- Auxiliary counts are for preserving stats from dead children and should not be confused with current local percpu counts.
- The file is explicitly legacy; adding new users would increase maintenance burden.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-cgroup-rwstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-cgroup.c -->
# File Research: sources/os/linux/linux/block/blk-cgroup.c

## Scope

This file implements the common block I/O controller cgroup core: blkcg/blkg allocation and teardown, cgroup callbacks, policy registration and disk activation, per-bio blkcg association, rstat-backed I/O accounting, optional async bio punting, and delay-based throttling.

## Core APIs and Entry Points

- Blkg/disk lifecycle:
  - `blkg_init_queue()`, `blkcg_init_disk()`, `blkcg_exit_disk()`.
  - Internal `blkg_alloc()`, `blkg_create()`, `blkg_lookup_create()`, `blkg_destroy()`, `blkg_destroy_all()`.
- Policy lifecycle:
  - `blkcg_policy_register()`, `blkcg_policy_unregister()`.
  - `blkcg_activate_policy()`, `blkcg_deactivate_policy()`.
- Configuration helpers:
  - `blkg_conf_init()`, `blkg_conf_open_bdev()`, `blkg_conf_open_bdev_frozen()`, `blkg_conf_prep()`, `blkg_conf_exit()`, `blkg_conf_exit_frozen()`.
- Stats:
  - `blk_cgroup_bio_start()`, `blkcg_print_blkgs()`, `__blkg_prfill_u64()`, `blkcg_print_stat()`.
- Bio association:
  - `bio_blkcg_css()`, `bio_associate_blkg_from_css()`, `bio_associate_blkg()`, `bio_clone_blkg_association()`.
- Delay/throttle:
  - `blkcg_add_delay()`, `blkcg_schedule_throttle()`, `blkcg_maybe_throttle_current()`, `blk_cgroup_congested()`.

## Major State

- Global:
  - `blkcg_root`, `blkcg_root_css`, `blkcg_policy[]`, `all_blkcgs`.
  - `blkcg_pol_register_mutex` serializes whole policy register/unregister operations.
  - `blkcg_pol_mutex` protects policy arrays and activation/deactivation.
  - `blkg_stat_lock` serializes stat propagation.
- Per blkcg:
  - `blkg_tree`, `blkg_hint`, `blkg_list`, per-policy `cpd[]`, `online_pin`, `congestion_count`, per-cpu `lhead` stat lists.
- Per blkg:
  - `q`, `blkcg`, `parent`, `refcnt`, online flag, per-cpu `iostat_cpu`, aggregate `iostat`, policy `pd[]`, delay accounting, RCU/free work.

## Control Flow

- `blkcg_init_disk()` waits for any old root blkg cleanup on shared queues, allocates the root blkg, creates it under queue lock, and stores `q->root_blkg`.
- Blkg creation walks from root down so every non-root blkg has a valid parent. Creation may return the closest existing blkg if allocation fails during lookup.
- Blkg destruction offlines per-policy data, removes cgroup tree/list links, clears hints, and kills the percpu ref. Actual freeing is RCU-delayed and then workqueue-delayed because policy free and queue release can sleep.
- Cgroup destruction is staged around writeback: offline writeback first, wait for `online_pin` release, destroy blkgs, then free the blkcg.
- `blk_cgroup_bio_start()` updates per-cpu bytes/ios, queues the per-cpu stat node on the blkcg lockless list, and notifies cgroup rstat.
- `__blkcg_rstat_flush()` drains only queued stat nodes, updates global blkg stats, and propagates deltas up the parent blkg chain.
- Policy activation freezes mq queues, allocates missing per-blkg policy data parent-first, handles GFP_NOWAIT failure by preallocating with GFP_KERNEL outside the queue lock, and rolls back on allocation failure.
- Delay throttling accumulates nanosecond delay per blkg; tasks are marked for notify-resume and sleep in user-return context rather than while holding I/O locks.

## Dependencies

- Cgroup core: css allocation/online/offline/free, cftypes, rstat, writeback integration.
- Block core: request queues, disks, queue freeze, `queue_lock`, `blkdev_get_no_open()`.
- Policy users include io priority and throttle code via `blk-ioprio.h` and `blk-throttle.h`.
- Kernel infra: radix tree, hlist/list, percpu refs, RCU, lockless llist, u64 stats, workqueues, PSI.

## Risks and Invariants

- Lock ordering is strict: queue lock nests outside blkcg lock in most paths; `blkcg_destroy_blkgs()` uses trylock/reschedule loops to avoid reverse-lock deadlocks.
- Blkg pointers are RCU protected, but only local stats/rate-limit fields are safe without a ref; queue and policy data require correct locks or refs.
- `blkg_conf_prep()` returns with queue lock held and must be paired with `blkg_conf_exit()`.
- Root cgroup stats are synthesized from disk stats rather than normally flushed blkg iostats.
- Bio association failure during cgroup teardown intentionally walks up to the closest live parent blkg.
- Delay code caps normal accumulated delay to 250 ms per syscall unless explicit non-decaying delay mode is used.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-cgroup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-cgroup.h -->
# File Research: sources/os/linux/linux/block/blk-cgroup.h

## Scope

This private header defines block-cgroup core structures, policy interfaces, blkg lookup/reference helpers, configuration context declarations, delay helpers, and no-op stubs for builds without `CONFIG_BLK_CGROUP`.

## Major Types

- `struct blkcg_gq` represents one block-cgroup/request-queue association.
- `struct blkcg` embeds the cgroup css and owns blkg lookup structures, policy cpd pointers, stat llist heads, optional FC app id, and writeback list.
- `struct blkg_policy_data` is per blkg per policy.
- `struct blkcg_policy_data` is per blkcg per policy.
- `struct blkcg_policy` is the policy registration record with cftypes and cpd/pd alloc/init/online/offline/free/stat callbacks.
- `struct blkg_conf_ctx` carries parsed per-device config state.

## Core Helpers

- `css_to_blkcg()` converts css to blkcg.
- `blkg_lookup()` resolves a blkcg/queue pair using root fast path, `blkg_hint`, then radix tree.
- `blkg_to_pd()`, `blkcg_to_cpd()`, `pd_to_blkg()`, `cpd_to_blkcg()` convert policy data references.
- `blkg_get()`, `blkg_tryget()`, `blkg_put()` wrap the blkg percpu ref.
- `blkg_for_each_descendant_pre/post` macros traverse online descendant blkgs under cgroup traversal.
- Delay helpers:
  - `blkcg_use_delay()`, `blkcg_unuse_delay()`.
  - `blkcg_set_delay()`, `blkcg_clear_delay()`.
- Merge helper:
  - `blk_cgroup_mergeable()` requires matching blkg and matching root-issue classification.
- `bio_issue_as_root_blkg()` classifies metadata and swap I/O as root-issued for priority inversion avoidance.

## Dependencies

- Public block-cgroup and cgroup headers, blk-mq, llist, and internal `blk.h`.
- Request operation helpers and queue policy bitsets.

## Risks and Invariants

- `blkg_lookup()` must be called under RCU or with queue lock conditions satisfying `rcu_dereference_check()`.
- `blkg_get()` assumes the caller already holds a valid reference; RCU lookups should use `blkg_tryget()`.
- `blkcg_set_delay()` uses negative `use_delay` as a mutually exclusive mode and must not be mixed with increment/decrement delay users.
- The disabled-configuration stubs preserve buildability but remove all cgroup behavior and make merges unconditionally cgroup-compatible.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-cgroup.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-core.c -->
# File Research: sources/os/linux/linux/block/blk-core.c

## Scope

This file is a central block-layer core implementation: request queue allocation/reference lifecycle, bio submission validation and recursion flattening, queue entry/freezing, block operation/status conversions, polling, disk I/O accounting, kblockd scheduling, plugging, and block subsystem initialization.

## Core APIs and Entry Points

- Queue state/lifecycle:
  - `blk_queue_flag_set()`, `blk_queue_flag_clear()`.
  - `blk_alloc_queue()`, `blk_get_queue()`, `blk_put_queue()`, `blk_queue_start_drain()`.
  - `blk_queue_enter()`, `__bio_queue_enter()`, `blk_queue_exit()`, `blk_sync_queue()`.
  - `blk_set_pm_only()`, `blk_clear_pm_only()`.
- Bio submission:
  - `submit_bio()`, `submit_bio_noacct()`, `submit_bio_noacct_nocheck()`.
  - Internal `__submit_bio()`, `__submit_bio_noacct()`, `__submit_bio_noacct_mq()`.
- Validation and remap:
  - `bio_check_ro()`, `bio_check_eod()`, `blk_partition_remap()`, `blk_check_zone_append()`, `blk_validate_atomic_write_op_size()`.
- Polling/accounting:
  - `bio_poll()`, `iocb_bio_iopoll()`.
  - `bdev_start_io_acct()`, `bio_start_io_acct()`, `bdev_end_io_acct()`, `bio_end_io_acct_remapped()`, `update_io_ticks()`.
- Plugging and workqueue:
  - `blk_start_plug_nr_ios()`, `blk_start_plug()`, `blk_finish_plug()`, `__blk_flush_plug()`, `blk_check_plugged()`.
  - `kblockd_schedule_work()`, `kblockd_mod_delayed_work_on()`.
- Initialization:
  - `blk_dev_init()` creates kblockd, queue slab cache, and block debugfs root.

## Major State

- `blk_debugfs_root`, exported block tracepoints.
- `blk_queue_ida` assigns queue ids used by blkcg lookup.
- `blk_requestq_cachep` allocates `struct request_queue`.
- `kblockd_workqueue` handles block async work.
- Operation-name and status conversion tables map `REQ_OP_*` and `BLK_STS_*`.

## Control Flow

- `submit_bio()` performs task/vm accounting and sets ioprio, then calls `submit_bio_noacct()`.
- `submit_bio_noacct()` checks NOWAIT support, crypto support, fault injection, read-only writes, end-of-device, partition remap, flush/FUA filtering, operation support, atomic write size, zone append constraints, and throttling before submission.
- `submit_bio_noacct_nocheck()` starts cgroup accounting and tracing, then either appends to `current->bio_list` during recursive submit or runs the mq/bio submit loop.
- Recursive submit loops convert recursive `submit_bio_noacct()` calls into iterative processing. For bio-based stacked drivers, newly submitted bios are sorted so lower-level queues are processed before same-level bios.
- `__submit_bio()` wraps actual submission in a plug, then either sends to blk-mq or calls `disk->fops->submit_bio()` after queue entry.
- Queue entry waits for freeze/PM resume unless NOWAIT is requested or the disk/queue is dying.
- `bio_poll()` can enter a frozen queue via direct percpu ref tryget to complete already submitted polled I/O during freezes.
- Plug flushing runs callbacks, flushes mq request lists, frees cached requests, and clears block timestamp state.

## Dependencies

- Block internals: blk-mq, sched, pm, cgroup/throttle/ioprio, integrity, crypto, part stats.
- Kernel subsystems: fault injection, debugfs, tracepoints, PM runtime, task I/O accounting, VM counters, workqueues.
- Disk/queue feature flags drive most validation decisions.

## Risks and Invariants

- `current->bio_list` recursion flattening is central to preventing stack overflows in stacked devices.
- Queue usage counters and freeze depth require ordering barriers to avoid missed wakeups.
- `REQ_OP_FLUSH` is not accepted directly as a bio op; flush bios enter as write with `REQ_PREFLUSH`.
- Metadata/swap/cgroup throttling and blk-crypto checks happen before actual lower-level submission.
- Plugging must be flushed on schedule/blocking paths to avoid reclaim and queue-freeze deadlocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-core.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-crypto-fallback.c -->
# File Research: sources/os/linux/linux/block/blk-crypto-fallback.c

## Scope

This file implements the blk-crypto software fallback using the kernel crypto API when hardware inline encryption does not support a raw-key configuration.

## Core APIs and Entry Points

- `blk_crypto_fallback_bio_prep()` prepares encrypted bios for fallback processing.
- `blk_crypto_fallback_start_using_mode()` lazily initializes fallback infrastructure and preallocates crypto transforms for a mode.
- `blk_crypto_fallback_evict_key()` evicts a fallback key through the shared crypto profile keyslot manager.
- Internal keyslot ops:
  - `blk_crypto_fallback_keyslot_program()`, `blk_crypto_fallback_keyslot_evict()`.
- Write path:
  - `blk_crypto_fallback_encrypt_bio()`, `__blk_crypto_fallback_encrypt_bio()`, `blk_crypto_alloc_enc_bio()`, `blk_crypto_fallback_encrypt_endio()`.
- Read path:
  - `blk_crypto_fallback_decrypt_endio()`, `blk_crypto_fallback_decrypt_bio()`, `__blk_crypto_fallback_decrypt_bio()`.

## Major State

- Module parameters:
  - `num_prealloc_bounce_pg`, `num_keyslots`, `num_prealloc_fallback_crypt_ctxs`.
- Fallback pools:
  - `bio_fallback_crypt_ctx_pool/cache`, `blk_crypto_bounce_page_pool`, `enc_bio_set`.
- Fallback keyslots:
  - `blk_crypto_keyslots[]` stores current mode and one skcipher tfm per supported mode.
  - `blk_crypto_fallback_profile` exposes fallback as a synthetic crypto profile.
- `blk_crypto_wq` runs read decryption in process context.
- `tfms_init_lock` and `tfms_inited[]` serialize lazy transform setup.
- `blank_key` is random bytes used to clear evicted tfm keys.

## Control Flow

- Fallback initialization creates an encrypted-bio bioset, synthetic crypto profile, workqueue, keyslot array, bounce-page pool, and fallback context mempool.
- Starting a mode allocates a sync skcipher transform for every fallback keyslot and publishes readiness with release/acquire ordering.
- For fallback writes, the original bio is consumed:
  - keyslot is obtained,
  - one or more encrypted bios are allocated,
  - source data units are encrypted into bounce pages using DUN-derived IVs,
  - encrypted bios are submitted,
  - completions free bounce pages and complete the source bio only after all encrypted bios finish.
- For fallback reads, `bi_private` and `bi_end_io` are wrapped. On successful I/O completion, decryption is queued to `blk_crypto_wq`, performed in place, then the original endio/private fields are restored.
- `blk_crypto_fallback_bio_prep()` clears the bio crypto context before submitting fallback reads so lower layers see ordinary bios.

## Dependencies

- Crypto API: `crypto_sync_skcipher`, skcipher requests, scatterlists.
- Generic blk-crypto profile/keyslot manager in `blk-crypto-profile.c`.
- Bio allocation, bvec iteration, cgroup association cloning, mempools, workqueues.

## Risks and Invariants

- Callers must call `blk_crypto_start_using_key()` before data path use; otherwise `tfms_inited[]` may be false and the bio fails.
- Fallback supports raw keys, not hardware-wrapped keys.
- Data segment length and offset must be aligned to the crypto data unit size.
- Write fallback can split one source bio into multiple encrypted bios; source completion depends on correct `__bi_remaining` accounting.
- The temporary page-pointer array is stored inside encrypted bio bvec memory; this relies on `PAGE_PTRS_PER_BVEC > 1`.
- Crypto transform allocation is kept out of the data path to avoid allocation deadlocks.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-crypto-fallback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-crypto-internal.h -->
# File Research: sources/os/linux/linux/block/blk-crypto-internal.h

## Scope

This internal header defines blk-crypto mode metadata, shared crypto helpers for bio/request merge and request lifecycle, sysfs declarations, fallback declarations, and compile-time stubs when inline encryption or fallback is disabled.

## Major Types and Declarations

- `struct blk_crypto_mode` describes each encryption mode’s display name, crypto API cipher string, key size, security strength, and IV size.
- `blk_crypto_modes[]` is declared for mode metadata.
- Inline-encryption declarations include:
  - sysfs register/unregister,
  - DUN increment and mergeability helpers,
  - keyslot get/put and eviction,
  - config support check,
  - ioctl dispatch.

## Core Helpers

- Merge checks:
  - `bio_crypt_ctx_back_mergeable()`, `bio_crypt_ctx_front_mergeable()`, `bio_crypt_ctx_merge_rq()`.
- Request state:
  - `blk_crypto_rq_set_defaults()`, `blk_crypto_rq_is_encrypted()`, `blk_crypto_rq_has_keyslot()`.
  - `blk_crypto_rq_get_keyslot()`, `blk_crypto_rq_put_keyslot()`, `blk_crypto_free_request()`.
  - `blk_crypto_rq_bio_prep()`.
- Bio state:
  - `bio_crypt_advance()`, `bio_crypt_free_ctx()`, `bio_crypt_do_front_merge()`.
- Fallback:
  - `blk_crypto_fallback_bio_prep()`, `blk_crypto_fallback_start_using_mode()`, `blk_crypto_fallback_evict_key()`.

## Dependencies

- Public `bio`, `blk-mq`, and blk-crypto types.
- `CONFIG_BLK_INLINE_ENCRYPTION` and `CONFIG_BLK_INLINE_ENCRYPTION_FALLBACK` determine whether helpers compile to real declarations or harmless stubs.

## Risks and Invariants

- Front merge must copy the incoming bio’s DUN into the request crypt context when inline encryption is enabled.
- Request crypto cleanup assumes keyslots are released before freeing request crypto context, with a warning fallback.
- Disabled inline encryption makes merge checks return true and crypto ioctl return `-ENOTTY`, preserving callers without crypto behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-crypto-internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-crypto-profile.c -->
# File Research: sources/os/linux/linux/block/blk-crypto-profile.c

## Scope

This file implements generic inline-encryption device profile and keyslot management. It lets storage drivers expose crypto capabilities and provides reusable keyslot allocation, programming, eviction, reprogramming, and capability composition.

## Core APIs and Entry Points

- Profile lifecycle:
  - `blk_crypto_profile_init()`, `devm_blk_crypto_profile_init()`, `blk_crypto_profile_destroy()`, `blk_crypto_register()`.
- Keyslot lifecycle:
  - `blk_crypto_get_keyslot()`, `blk_crypto_put_keyslot()`, `blk_crypto_keyslot_index()`.
  - `__blk_crypto_evict_key()`, `blk_crypto_reprogram_all_keys()`.
- Capability helpers:
  - `__blk_crypto_cfg_supported()`, `blk_crypto_intersect_capabilities()`, `blk_crypto_has_capabilities()`, `blk_crypto_update_capabilities()`.
- Hardware-wrapped key operations:
  - `blk_crypto_derive_sw_secret()`, `blk_crypto_import_key()`, `blk_crypto_generate_key()`, `blk_crypto_prepare_key()`.

## Major State

- `struct blk_crypto_keyslot` stores slot refcount, idle LRU node, hash node, key pointer, and owning profile.
- `struct blk_crypto_profile` owns:
  - profile rwsem and lockdep key,
  - optional device pointer for runtime PM,
  - keyslot array,
  - idle slot list and waitqueue,
  - key hash table,
  - low-level driver ops and capability fields.

## Control Flow

- Profile initialization zeroes the profile, creates a dynamic lock class, initializes the rwsem, and optionally allocates keyslot and hash-table state.
- `blk_crypto_get_keyslot()`:
  - returns immediately if the device has no keyslot concept,
  - first attempts a read-locked lookup and ref grab,
  - otherwise enters hardware section with runtime PM and write lock,
  - waits for idle slots if necessary,
  - programs a slot via driver `keyslot_program`,
  - hashes it by key pointer and removes it from idle LRU.
- `blk_crypto_put_keyslot()` decrements the slot refcount and returns it to idle LRU when the count reaches zero.
- `__blk_crypto_evict_key()` calls driver eviction, warns if the key is still referenced, and unlinks the key from hash state even if eviction errors.
- Hardware-wrapped key helpers validate profile support and delegate under the same runtime-PM/write-lock wrapper.
- Capability intersection clears any parent capability not supported by a child; capability update assumes shrinking is externally synchronized.

## Dependencies

- Driver-provided `struct blk_crypto_ll_ops`.
- Runtime PM, rwsems, waitqueues, spinlocks, hlist/list, kvzalloc/kvmalloc.
- Block integrity check in `blk_crypto_register()` disallows integrity and hardware inline encryption together.

## Risks and Invariants

- Calling into hardware requires the device resumed before taking `profile->lock`, because runtime resume can reprogram keys and interact with the same lock.
- Key identity is pointer-based; upper layers must not free a key before eviction and before I/O using it has completed.
- Slot refs must be zero before eviction; nonzero refs indicate a kernel bug and return `-EBUSY`.
- Drivers that lose keys on reset must call `blk_crypto_reprogram_all_keys()`.
- Devices cannot shrink advertised crypto capabilities while bios relying on old capabilities may still be in flight.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-crypto-profile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-crypto-sysfs.c -->
# File Research: sources/os/linux/linux/block/blk-crypto-sysfs.c

## Scope

This file exposes blk-crypto capabilities through `/sys/block/$disk/queue/crypto/`.

## Core APIs

- `blk_crypto_sysfs_register()` creates the `crypto` kobject under a disk queue kobject if the queue has a crypto profile.
- `blk_crypto_sysfs_unregister()` drops that kobject.
- `blk_crypto_sysfs_init()` initializes dynamic encryption-mode attributes at boot.

## Sysfs Surface

- Top-level read-only files:
  - `hw_wrapped_keys` appears only if hardware-wrapped keys are supported and prints `supported`.
  - `raw_keys` appears only if raw keys are supported and prints `supported`.
  - `max_dun_bits` prints `8 * max_dun_bytes_supported`.
  - `num_keyslots` prints `profile->num_slots`.
- `modes/` subdirectory:
  - one read-only file per valid encryption mode,
  - visible only if `profile->modes_supported[mode]` is nonzero,
  - prints the supported data-unit-size bitmask as hex.

## Major State

- `struct blk_crypto_kobj` embeds kobject and profile pointer.
- `struct blk_crypto_attr` wraps sysfs attribute plus a profile-aware show callback.
- Dynamic arrays `__blk_crypto_mode_attrs[]` and `blk_crypto_mode_attrs[]` avoid hard-coding mode filenames.

## Dependencies

- `blk_crypto_modes[]` for mode names.
- `struct blk_crypto_profile` capability fields.
- sysfs/kobject attribute group infrastructure.

## Risks and Invariants

- Mode initialization assumes `BLK_ENCRYPTION_MODE_INVALID == 0` and skips index 0.
- Attribute visibility depends on current profile fields; capability shrinking without upper-layer synchronization has the same risk described in profile management.
- `blk_crypto_sysfs_unregister()` assumes the kobject pointer is either valid or safely accepted by `kobject_put()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-crypto-sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-crypto.c -->
# File Research: sources/os/linux/linux/block/blk-crypto.c

## Scope

This file implements blk-crypto bio/request context handling, supported encryption mode definitions, key initialization, native-vs-fallback decision logic, key eviction, and user ioctls for hardware-wrapped key operations.

## Core APIs and Entry Points

- Mode and context setup:
  - `blk_crypto_modes[]`.
  - `bio_crypt_set_ctx()`, `__bio_crypt_free_ctx()`, `__bio_crypt_clone()`.
  - `blk_crypto_init_key()`.
- DUN/merge helpers:
  - `bio_crypt_dun_increment()`, `__bio_crypt_advance()`, `bio_crypt_dun_is_contiguous()`.
  - `bio_crypt_rq_ctx_compatible()`, `bio_crypt_ctx_mergeable()`.
- Request integration:
  - `__blk_crypto_rq_get_keyslot()`, `__blk_crypto_rq_put_keyslot()`, `__blk_crypto_free_request()`, `__blk_crypto_rq_bio_prep()`.
- Submission/configuration:
  - `__blk_crypto_submit_bio()`.
  - `blk_crypto_config_supported_natively()`, `blk_crypto_config_supported()`, `blk_crypto_start_using_key()`.
  - `blk_crypto_evict_key()`.
- Ioctls:
  - `blk_crypto_ioctl()` dispatches import/generate/prepare wrapped-key commands.

## Major State

- Supported modes include AES-256-XTS, AES-128-CBC-ESSIV, Adiantum, and SM4-XTS with cipher strings, key sizes, security strengths, and IV sizes.
- `bio_crypt_ctx_cache` and `bio_crypt_ctx_pool` allocate bio/request crypto contexts.
- Module parameter `num_prealloc_crypt_ctxs` sizes the context mempool.

## Control Flow

- `bio_crypt_ctx_init()` creates the context cache/mempool and validates mode definitions at boot.
- Bio crypto contexts hold a key pointer and DUN array. Advancing a bio increments the DUN by data units.
- Mergeability requires matching key pointer and contiguous DUN sequence.
- `__blk_crypto_submit_bio()` fails encrypted bios with no data; if native support is absent, it uses fallback when enabled and the key type is supported.
- `blk_crypto_start_using_key()` must be called by upper layers before I/O to ensure native support or preallocated fallback transforms.
- `blk_crypto_evict_key()` evicts from native profile or fallback, logs errors, and returns void because callers cannot recover meaningfully.
- Wrapped-key ioctls copy arguments from userspace, validate reserved fields and sizes, call profile operations, copy generated material back, and zero temporary key buffers.

## Dependencies

- `blk-crypto-profile.c` for profiles, keyslots, and wrapped-key operations.
- `blk-crypto-fallback.c` for software fallback.
- Bio and request crypto hooks from `blk-crypto-internal.h`.
- Userspace ABI structures and ioctl numbers from public blk-crypto headers.

## Risks and Invariants

- `bio_crypt_set_ctx()` expects a reclaimable GFP mask so mempool allocation cannot fail.
- Key pointers, not key bytes, define merge/keyslot identity.
- DUN wraparound is not treated as contiguous.
- Fallback only supports raw keys; hardware-wrapped keys require native hardware support.
- ioctl paths must zero stack key buffers on all exits, which this file does with `memzero_explicit()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/block/blk-flush.c -->
# File Research: sources/os/linux/linux/block/blk-flush.c

## Scope

This file implements sequencing for block requests with `REQ_PREFLUSH` and/or `REQ_FUA`, translating them into optional preflush, data, and postflush phases according to queue write-cache and FUA capabilities.

## Core APIs and Entry Points

- Flush state machine:
  - `blk_insert_flush()` inserts a request into flush sequencing or lets it continue normally.
  - `blk_flush_complete_seq()` advances one request through its next phase.
  - `blk_kick_flush()` decides when to issue the shared flush request.
  - `flush_end_io()` completes the shared flush request and advances all requests waiting on it.
  - `mq_flush_data_end_io()` handles completion of the data phase for sequenced requests.
- Utilities:
  - `is_flush_rq()` identifies the shared flush request by end_io callback.
  - `blkdev_issue_flush()` submits a synchronous flush bio.
  - `blk_alloc_flush_queue()`, `blk_free_flush_queue()`.
  - `blk_mq_hctx_set_fq_lock_class()` lets drivers customize flush lockdep class.

## Major State

- Sequence bits:
  - `REQ_FSEQ_PREFLUSH`, `REQ_FSEQ_DATA`, `REQ_FSEQ_POSTFLUSH`, `REQ_FSEQ_DONE`.
- `struct blk_flush_queue` owns:
  - double-buffered `flush_queue[2]`,
  - pending/running indexes,
  - `flush_pending_since`,
  - `flush_data_in_flight`,
  - shared `flush_rq`,
  - `mq_flush_lock`,
  - saved flush request status.

## Control Flow

- `blk_insert_flush()` computes required policy:
  - data phase if the request has sectors,
  - preflush if writeback cache exists and `REQ_PREFLUSH` is set,
  - postflush if writeback cache exists, `REQ_FUA` is set, and hardware lacks FUA.
- It clears `REQ_PREFLUSH` and unsupported `REQ_FUA` before driver submission, and sets `REQ_SYNC` to preserve accounting semantics.
- Requests needing only data return false and proceed normally.
- Requests needing pre/post flush enter the state machine with `RQF_FLUSH_SEQ` and a saved original end_io.
- Double-buffering lets multiple requests wait on one shared `REQ_OP_FLUSH` request. `blk_kick_flush()` issues a flush only when no other flush is running and either no data phase is in flight or pending flushes have waited past `FLUSH_PENDING_TIMEOUT`.
- The shared flush request borrows tag/internal tag context from the first pending request and is submitted through the queue requeue path.
- Data-phase completion restores queue list state, decrements in-flight data, and advances to postflush or done.
- Final completion restores the original request bio/end_io state and calls `blk_mq_end_request()`.

## Dependencies

- blk-mq request lifecycle, tags, requeue list, scheduler restart, and request initialization.
- Queue feature flags `BLK_FEAT_FUA` and write-cache state.
- Partition stats for flush accounting.

## Risks and Invariants

- Flush/FUA requests must not be normally merged; the code warns if `rq->bio != rq->biotail`.
- Sequenced data requests are completed twice internally, but bio submitters are notified only after the full flush sequence completes.
- The state machine requires `fq->mq_flush_lock` for sequence/queue transitions.
- The shared flush request is reused and must be marked idle only after true completion because timeout paths may call its end_io.
- Tag borrowing differs for scheduler vs no-scheduler queues and must be unwound correctly.
<!-- END FILE RESEARCH: sources/os/linux/linux/block/blk-flush.c -->