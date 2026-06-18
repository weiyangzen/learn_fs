# subset-b-007658 research

Grouped research for Lustre llite PCC and read/write page-cache support. Each file section preserves the source path and is bounded for reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/pcc.c -->
# sources/distributed-fs/lustre-release/lustre/llite/pcc.c

## Purpose

`pcc.c` implements Lustre llite Persistent Client Cache support. It manages client-local cache backends, policy parsing, automatic and ioctl-driven attachment, detachment, open/read/write/getattr/setattr/fsync/splice/mmap interception, and local copy lifecycle. The file supports two caching modes: PCC-RW, where a single client uses a local read-write copy synchronized through HSM archive semantics, and PCC-RO, where read-only local copies can be attached on multiple clients after setting/observing read-only layout state.

## Important APIs, types, and functions

The public entry points are declared in `pcc.h` and implemented here: `pcc_super_init()`, `pcc_super_fini()`, `pcc_cmd_handle()`, `pcc_super_dump()`, `pcc_readwrite_attach()`, `pcc_readwrite_attach_fini()`, `pcc_ioctl_attach()`, `pcc_ioctl_detach()`, `pcc_ioctl_state()`, `pcc_file_open()`, `pcc_file_release()`, `pcc_file_read_iter()`, `pcc_file_write_iter()`, `pcc_inode_getattr()`, `pcc_inode_setattr()`, `pcc_file_splice_read()`, `pcc_fsync()`, `pcc_file_mmap()`, `pcc_vm_open()`, `pcc_vm_close()`, `pcc_fault()`, `pcc_page_mkwrite()`, `pcc_inode_create()`, `pcc_inode_create_fini()`, `pcc_create_attach_cleanup()`, `pcc_dataset_match_get()`, `pcc_dataset_put()`, `pcc_inode_free()`, and `pcc_layout_invalidate()`.

The configuration path parses commands of the form `add <absolute path> <rule> key=value...`, `del <absolute path>`, and `clear`. Match rules are parsed as disjunctions of conjunctions, with expressions over `uid`, `gid`, `projid`, `fname`/`filename`, `size`, and `mtime`. Operators are `=`, `<`, and `>`, with equality list support for IDs, sizes, and names. `pcc_dataset_add()` validates server support and dataset flags, resolves the backend path with `kern_path()`, copies rule state, checks duplicate path/archive IDs, and installs the dataset under `pccs_rw_sem`. `pcc_super_dump()` emits YAML-like state for proc/debug consumers.

Attachment helpers include `pcc_dataset_get()`, `pcc_try_dataset_attach()`, `pcc_try_datasets_attach()`, `pcc_try_auto_attach()`, `pcc_try_readonly_open_attach()`, `pcc_readonly_attach_sync()`, `pcc_readonly_attach_async()`, and `pcc_readwrite_attach()`. Local object helpers include `pcc_fid2dataset_path()`, `pcc_lookup()`, `pcc_mkdir_p()`, `pcc_create()`, `pcc_inode_remove()`, `pcc_attach_data_archive()`, and `pcc_copy_data()`.

The I/O interceptors redirect operations to `struct pcc_file::pccf_file` when `pcc_io_init()` finds or auto-attaches a valid `struct pcc_inode`. `pcc_io_fini()` decrements `pcci_active_ios`, wakes detach/mmap waiters, and decides whether a failed PCC operation can be tolerated by falling back to normal Lustre I/O.

## Control flow

Mount/superblock setup calls `pcc_super_init()`, preparing a restricted credential used for backend filesystem operations and initializing the dataset list, generation, async threshold, and permission mode. Configuration writes call `pcc_cmd_handle()`, which parses a command into `struct pcc_cmd`, applies add/delete/clear, and frees command-owned rule state.

Open starts in `pcc_file_open()`. Regular files are considered only if encryption policy allows PCC. If an attach is already in progress the file is marked fallback. Otherwise existing `pcc_inode` layout is used, `pcc_try_auto_attach()` is attempted when generation/dataset flags allow it, and read-only policy attach may be attempted for read-only opens. On success the local backend file is opened with `dentry_open()` and stored in per-file data.

For read, write, stat, setattr, splice, fsync, mmap fault, and page-mkwrite paths, the common pattern is: initialize cached/fallback decision with `pcc_io_init()` or `pcc_mmap_io_init()`, call the backing file or backing vm operation when cached, then run `pcc_io_fini()`. RO cached files detach on write/setattr/page-mkwrite. RW write failures for `-ENOSPC` or `-EDQUOT` are not tolerated; most other eligible failures detach/fallback according to mode and operation.

PCC-RO attach first sets or verifies the Lustre read-only layout with `pcc_layout_rdonly_set()`, copies data from Lustre into a newly created PCC file, installs a `pcc_inode`, writes `user.PCC.layout`, and optionally records encrypted cleartext size in `user.PCC.encsize`. Large RO attachments may run in a kthread via `pcc_readonly_attach_async()`. PCC-RW attach creates/copies the local file, installs `pcc_inode`, then `pcc_readwrite_attach_fini()` records the layout generation after the HSM/layout side succeeds.

Detach uses `pcc_ioctl_detach()`. RW detach may request HSM remove/restore cleanup; RO detach clears the layout, may unlink the local copy, and drops the `pcc_inode` reference. `pcc_layout_invalidate()` performs similar detach when Lustre layout locks are revoked.

## State and persistence behavior

`struct pcc_super` persists client-side dataset configuration in memory and increments `pccs_generation` on removal/clear. Each `ll_inode_info` tracks `lli_pcc_inode`, `lli_pcc_state`, cached dataset flags, generation, mmap count, and fallback mmap-negative count. `struct pcc_inode` holds a backend `struct path`, refcount, PCC type, layout generation, active I/O count, waitqueue, and flags for attribute validity and unlink state.

On-disk state lives in backend filesystem paths derived from FID and HSM tool layout. `user.PCC.layout` stores the Lustre layout generation for auto reattach validation. `user.PCC.encsize` stores cleartext file size for encrypted PCC-RO copies whose local file contains ciphertext aligned to encryption units. Dataset rules and backend paths are not persisted by this file beyond the live `pcc_super` list.

Mmap is stateful and high-risk: for PCC mmap, Lustre may temporarily switch the Lustre inode mapping operations and host to the PCC inode mapping so page faults operate on the local backend. Detach waits for active I/O and resets mapping state, writes dirty pages, truncates page cache, restores `ll_aops`, and returns the PCC inode to its own `i_data` mapping.

## Dependencies and integration points

This file depends on llite internals (`ll_i2info`, `ll_i2sbi`, `ll_i2pccs`, `ll_layout_refresh`, `ll_layout_restore`, `ll_layout_write_intent`, stats counters), CLIO layout inspection (`cl_object_layout_get`), HSM ioctl paths (`LL_IOC_HSM_REQUEST`), VFS helpers (`dentry_open`, `lookup_noperm`, `vfs_create`, `vfs_unlink`, `notify_change`, xattrs), kernel credentials, kthreads, mmap `vm_operations_struct`, and Lustre encryption helpers (`llcrypt_decrypt_block_inplace`, `ll_has_encryption_key`, `S_PCCCOPY`). It integrates with llite file private data through `struct pcc_file`, with inode teardown through `pcc_inode_free()`, and with layout lock cancellation via `pcc_layout_invalidate()`.

## Risks and edge cases

Major risks are races among attach, detach, layout revocation, mmap faults, and open. These are mitigated by `lli_pcc_lock`, `PCC_STATE_FL_ATTACHING`, layout generation checks, `pcci_active_ios`, and waitqueues, but the code still contains explicit race failpoints. Backend filesystem semantics are another risk: project quota support may be absent and is disabled after `-EOPNOTSUPP`/`-ENOTTY`; mmap private data conflicts cause `-EOPNOTSUPP`; direct user access to PCC backend files is called out as a FIXME because shared mappings can be unsafe. Encrypted PCC-RO needs careful ciphertext/cleartext size handling and page-cache truncation to avoid stale plaintext. Auto attach can mark `PCC_DATASET_NONE` after misses, suppressing later attempts until generation changes or manual attach.

## Test signals

Useful test signals include proc command parsing for add/delete/clear, rule matching by UID/GID/project/name/size/mtime, duplicate dataset rejection, generation bumping, PCC-RO attach on read-only open, async attach threshold behavior, RW attach/fini with layout generation mismatch, detach with and without `PCC_DETACH_FL_UNCACHE`, encrypted PCC-RO read/decrypt and `encsize`, mmap attach/fault/page_mkwrite/detach retry behavior, failpoints such as `OBD_FAIL_LLITE_PCC_FAKE_ERROR`, `OBD_FAIL_LLITE_PCC_MKWRITE_PAUSE`, `OBD_FAIL_LLITE_PCC_DETACH_MKWRITE`, and stats counters `LPROC_LL_PCC_ATTACH`, `LPROC_LL_PCC_ATTACH_BYTES`, `LPROC_LL_PCC_HIT_BYTES`, `LPROC_LL_PCC_AUTOAT`, and `LPROC_LL_PCC_DETACH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/pcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/pcc.h -->
# sources/distributed-fs/lustre-release/lustre/llite/pcc.h

## Purpose

`pcc.h` is the interface and data model for llite Persistent Client Cache. It defines dataset policy structures, superblock and inode/file runtime state, mmap wrapper state, attach context, I/O operation classification, user command representation, and the exported PCC functions consumed by llite open, close, I/O, mmap, ioctl, create, and inode cleanup paths.

## Important APIs, types, and functions

Policy parsing and matching types are `struct pcc_match_id`, `struct pcc_match_size`, `struct pcc_match_fname`, `enum pcc_field`, `enum pcc_field_op`, `struct pcc_expression`, `struct pcc_conjunction`, `struct pcc_match_rule`, and `struct pcc_matcher`. They model a disjunction of conjunctions over UID, GID, project ID, filename wildcard, file size, and modification age.

Dataset and global state are represented by `enum pcc_dataset_flags`, `struct pcc_dataset`, and `struct pcc_super`. Important flags include `PCC_DATASET_OPEN_ATTACH`, `PCC_DATASET_IO_ATTACH`, `PCC_DATASET_STAT_ATTACH`, `PCC_DATASET_PCCRW`, `PCC_DATASET_PCCRO`, `PCC_DATASET_MMAP_CONV`, `PCC_DATASET_PROJ_QUOTA`, and `PCC_DATASET_NONE`. `struct pcc_super` owns the dataset list, credentials, generation, async attach threshold, affinity flag, and mode bits used by `pcc_inode_permission()`.

Per-object runtime state is split across `struct pcc_inode`, `struct pcc_file`, and `struct pcc_vma`. `pcc_inode` is tied to `ll_inode_info` and stores the backend path, refcount, PCC type, layout generation, active I/O count, waitqueue, and detach/unlink state. `pcc_file` stores the opened backend file and whether a specific open file must fall back. `pcc_vma` wraps backend vm ops and original Lustre file state for mmap.

The exported API covers superblock lifecycle, command handling, dataset matching, attach/detach/state ioctls, file open/release, read/write/splice/fsync, getattr/setattr, mmap vm hooks, create-time RW attach, dataset refcounting, inode cleanup, and layout invalidation.

## Control flow

Most llite call sites treat these APIs as optional front-end hooks. File open initializes `struct pcc_file` with `pcc_file_init()`, calls `pcc_file_open()`, and later calls `pcc_file_release()`. Read/write-like paths call the corresponding `pcc_*` function with a `bool *cached`; if it returns with `cached == false`, normal Lustre I/O continues. Mmap paths use `pcc_file_mmap()` at mmap setup and `pcc_vm_open()`, `pcc_vm_close()`, `pcc_fault()`, and `pcc_page_mkwrite()` from vm operations. Create paths can use `pcc_inode_create()` and `pcc_inode_create_fini()` to make and attach a local RW PCC copy.

## State and persistence behavior

The header defines in-memory ownership and persistence boundaries. Dataset configuration is live in `pcc_super`, protected by `pccs_rw_sem`, and versioned by `pccs_generation`. `pcc_inode` stores the backend `struct path` and layout generation that `pcc.c` also persists in local xattrs. `pcc_file` is per-open state and tracks local file handles plus fallback. `pcc_vma` reference counts mmap wrappers and preserves backend vm operations. No code in the header itself persists state, but the structures are designed around the `user.PCC.layout` and `user.PCC.encsize` persistence in `pcc.c`.

## Dependencies and integration points

The header depends on Linux VFS/MM types, Lustre user ABI types from `lustre_user.h`, HSM tool type enums, `struct ll_inode_info`, `struct ll_sb_info`, `struct cl_layout`, `struct lu_fid`, VM fault types, pipe splice types, and Lustre PCC user ioctl structs. It is included by `pcc.c` and llite implementation files that need to call PCC hooks.

## Risks and edge cases

The key risk is that many fields encode locking and reference-count assumptions not enforced by the type system. `pcci_refcount == 0` means uninitialized and `1` means attached with no user, so callers must use the helper lifecycle. `pcci_active_ios` and `pcci_waitq` must bracket every redirected operation. `pccf_fallback` interacts with inode-level mmap-negative counters, so missed reset paths can suppress PCC use. `pcc_vma_file()` depends on `vm_private_data` containing a valid `struct pcc_vma`, but falls back to `vma->vm_file` when absent.

## Test signals

Compile coverage across kernel feature macros is important because declarations include folio/page, mmap, splice, and ioctl-facing APIs. Runtime tests should observe `cached` booleans, per-open fallback reset, mmap open/close refcounts, attach/detach state reporting, and generation-driven auto attach eligibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/pcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/rw.c -->
# sources/distributed-fs/lustre-release/lustre/llite/rw.c

## Purpose

`rw.c` implements Lustre llite shared page-cache read/write support across kernel versions. It owns client readahead budgeting, readahead pattern detection, readpage integration with CLIO, asynchronous readahead work, writeback submission through CLIO, and per-thread CLIO context lookup used by readpage/direct-I/O/write-begin code.

## Important APIs, types, and functions

Important exported functions are `ll_ra_count_put()`, `ll_ra_stats_inc()`, `ll_readahead_init()`, `ll_ras_enter()`, `ll_writepages()`, `ll_cl_find()`, `ll_cl_add()`, `ll_cl_remove()`, `ll_io_read_page()`, `ll_readpage()`, and optionally `ll_read_folio()`. Internal helpers include `ll_ra_count_get()`, `ll_read_ahead_page()`, `stride_page_count()`, `ria_page_count()`, `ras_align()`, `ll_read_ahead_pages()`, `ll_readahead_handle_work()`, `ll_readahead()`, `ll_readpages()`, `ras_reset()`, `ras_stride_reset()`, `ras_detect_read_pattern()`, `ras_update()`, `kickoff_async_readahead()`, and `ll_use_fast_io()`.

The file manipulates `struct ll_readahead_state`, `struct ll_ra_info`, `struct ra_io_arg`, `struct ll_readahead_work`, `struct ll_cl_context`, CLIO `struct cl_io`, `struct cl_page`, `struct cl_2queue`, `struct cl_read_ahead`, and VVP environment state.

## Control flow

Buffered reads enter `ll_readpage()` or `ll_read_folio()`. If the current thread has no `ll_cl_context`, the function attempts a fast cached-page path by finding an existing CLIO page, checking `cp_defer_uptodate`, updating readahead state on cache hit, optionally starting async readahead, marking the VM page uptodate, and unlocking it. If an active CLIO context exists, `ll_readpage()` validates truncation and lock coverage edge cases, asserts kernel readahead is disabled, handles direct-read fallback restart conditions, wraps the VM page in a CLIO page, and calls `ll_io_read_page()`.

`ll_io_read_page()` updates readahead state, queues the requested page if not already uptodate, optionally expands the queue with `ll_readahead()` or `ll_readpages()`, submits queued pages with `cl_io_submit_rw()`, waits for synchronous completion of the trigger page, discards unsent or temporary queue pages, and releases readahead locks.

Readahead policy starts with `ll_ras_enter()` when higher layers observe user read position and size. It tracks consecutive requests, whole-file-read eligibility, loose sequential reads, stride reads, and mmap cluster reads. `ras_update()` reacts to actual page hits/misses and grows or resets the window. `ll_readahead()` reserves global readahead budget, clamps to KMS/EOF, checks lock coverage with `cl_io_read_ahead_prep()`, queues pages, and advances `ras_next_readahead_idx`. `ll_readahead_handle_work()` performs the same work from a workqueue for async readahead.

Writeback enters `ll_writepages()`, maps kernel writeback reasons to CLIO fsync modes/priorities, skips freed/no-object inodes, calls `cl_sync_file_range()`, and updates `mapping->writeback_index` for cyclic or whole-file writeback.

## State and persistence behavior

The main persistent runtime state is in memory: per-superblock `ll_ra_info` tracks global and per-file readahead limits, current reserved pages, async queue, and stats; per-file `fd_ras` tracks window start, size, next index, RPC size, stride offsets, consecutive access counts, mmap range detection, and async last index. Page state is stored in CLIO pages and Linux page flags (`PageUptodate`, `cp_defer_uptodate`, `cp_ra_used`, `cp_ra_updated`). No durable on-disk state is written here; writeback delegates persistence to CLIO/OSC through `cl_sync_file_range()` and `cl_io_submit_rw()`.

## Dependencies and integration points

The file depends on llite internal inode/superblock/file structures, CLIO object/page/I/O APIs, VVP environment state, LNet/Lustre constants such as `PTLRPC_MAX_BRW_PAGES`, Linux page cache APIs, workqueues, writeback control, task I/O accounting, and lprocfs counters. It integrates with `rw26.c` through `ll_readpage()`, `ll_read_folio()`, `ll_writepages()`, and `ll_cl_find()`, with high-level read/write paths via `ll_cl_add()`/`ll_cl_remove()`, and with PCC mmap safeguards because PCC forces kernel readahead counters to zero before shared mapping use.

## Risks and edge cases

Readahead budget accounting is delicate: `ll_ra_count_get()` intentionally over-reserves minimum pages for performance, so callers must always return unused `ria_reserved`. Stride and mmap cluster detection can over-prefetch or reset too aggressively. The fast read path depends on valid CLIO page identity and layout assumptions. There are explicit workarounds for kernel 5.12 read batching adding an extra page, for truncated pages racing with lock cancellation, and for direct I/O falling back to buffered I/O under lockless mode. Kernel readahead must remain disabled; unexpected `ra_pages`/`io_pages` triggers assertions.

## Test signals

Relevant signals are lprocfs readahead stats (`RA_STAT_HIT`, `MISS`, `READAHEAD_PAGES`, `FORCEREAD_PAGES`, `ASYNC`, `EOF`, `MAX_IN_FLIGHT`, `FAILED_FAST_READ`, `MMAP_RANGE_READ`, `MISS_IN_WINDOW`), fast-read hit/miss behavior, async readahead inflight accounting, KMS/EOF clamping, stride read windows, mmap clustered faults, cyclic writeback index updates, direct-read fallback restart `-ENOLCK`, failpoints `OBD_FAIL_LLITE_READPAGE_PAUSE` and `OBD_FAIL_LLITE_READPAGE_PAUSE2`, and assertions that kernel readahead remains disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/rw26.c -->
# sources/distributed-fs/lustre-release/lustre/llite/rw26.c

## Purpose

`rw26.c` provides Linux address-space-operation glue for Lustre llite on 2.6-style and newer kernels. It connects VM page invalidation/release, direct I/O, buffered write begin/end, dirty/writeback behavior, readpage/read_folio, and page migration policy to the shared CLIO logic in `rw.c`.

## Important APIs, types, and functions

The central export is `const struct address_space_operations ll_aops`, which installs dirty-page handling, invalidate, readpage/read_folio, releasepage/release_folio, `direct_IO`, `writepages`, `write_begin`, `write_end`, and optional `migrate_folio`. Important helpers include `ll_invalidate_folio()` or `ll_invalidatepage()`, `do_release_page()`, `ll_release_folio()` or `ll_releasepage()`, `ll_iov_iter_is_unaligned()`, `ll_direct_rw_pages()`, `ll_direct_IO()`, `ll_prepare_partial_page()`, `ll_tiny_write_begin()`, `ll_write_begin()`, `ll_tiny_write_end()`, `ll_write_end()`, and `ll_migrate_folio()`.

## Control flow

Invalidate and release operations run under locked, non-writeback pages. Full invalidation finds the CLIO page for each VM page in a folio/page and deletes it with `cl_page_delete()`. Release refuses dirty/writeback pages, drops unused CLIO pages, and avoids object deletion hazards while using percpu CLIO environments.

Direct I/O enters `ll_direct_IO()` from the kernel address-space op while a CLIO context is active. It checks alignment, EOF, server/client unaligned-DIO support, AIO restrictions, pipe iterators, lockless/parallel constraints, and maximum sub-I/O size. For each segment it allocates `struct cl_sub_dio`, pins/initializes pages with `cl_dio_pages_init()`, wraps them as transient CLIO pages in `ll_direct_rw_pages()`, submits with `cl_dio_submit_rw()`, optionally waits synchronously, advances the iterator, and accounts bytes in VVP state. Unaligned ENOMEM can drain in-flight sub-DIOs and retry.

Buffered writes use `ll_write_begin()` and `ll_write_end()`. `write_begin` finds the active CLIO context, handles direct-I/O fallback restart, avoids deadlock by committing existing dirty queues before blocking on dirty/writeback pages, obtains or creates the VM page, wraps it as a cacheable CLIO page, owns it, and reads old data for partial-page writes through `ll_prepare_partial_page()` unless the page is fully overwritten or beyond KMS. Without a CLIO context, a tiny-write path only accepts an already present uptodate dirty page. `write_end` queues copied pages into VVP write queues, marks inode dirty, chooses urgent priority under cgroup writeback pressure, commits on full RPC/sync/dirty-page pressure, or disowns and releases the page if nothing was copied.

## State and persistence behavior

This file manages transient page and direct-I/O state rather than durable metadata. It updates Linux page flags, CLIO page ownership, CLIO sync anchors, VVP read/write byte counters, VVP queued write ranges, and inode dirty state. Persistence of data is delegated to CLIO submit/commit and `ll_writepages()` from `rw.c`. Direct I/O uses transient CLIO pages and optional encrypted-inode references for llcrypt. Buffered writes preserve old page contents for partial updates by reading from storage when KMS indicates existing data.

## Dependencies and integration points

`rw26.c` depends on Linux address-space operations, folio compatibility macros, page cache helpers, direct-I/O iterators, writeback/cgroup writeback, migration hooks, llite internal structures, and CLIO/VVP functions from Lustre. It calls `ll_readpage()`, `ll_read_folio()`, `ll_writepages()`, `ll_cl_find()`, and `ll_io_read_page()` from `rw.c`. It also participates in PCC because `pcc_inode_mapping_reset()` restores `mapping->a_ops = &ll_aops` after PCC mmap detaches, and because PCC disables kernel readahead before using shared mappings.

## Risks and edge cases

The highest-risk areas are direct-I/O fallback and page ownership. Lockless direct I/O that falls back to buffered I/O must request restart with `ci_dio_lock` to avoid mixing lockless DIO and LDLM-buffered reads/writes. Unaligned DIO is restricted for AIO and pipes, and unsupported servers force buffered fallback. Write begin must avoid deadlocks when dirty pages are already queued and grant allocation may be needed. Partial-page writes must handle truncation (`-EAGAIN`) and KMS correctly. Migration is intentionally failed with `-EIO`, so memory-management behavior depends on reclaim/release instead of migrate.

## Test signals

Tests should cover full and partial invalidate/release, direct I/O aligned and unaligned reads/writes, EOF clipping, pipe iterator fallback, AIO unaligned rejection, unaligned ENOMEM drain/retry, lockless-to-locked restart via `-ENOLCK`, direct write fallback with designated mirrors returning `-EBUSY`, partial-page write read-before-write, full-page overwrite avoiding read, dirty/writeback page deadlock avoidance, cgroup dirty-exceeded urgent commit, migration failure, and the shape of `ll_aops` under kernel feature macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/rw26.c -->
