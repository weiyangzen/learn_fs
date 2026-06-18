# Group Research: group_307_dragonflybsd_sources_os_bsd_dragonflybsd_sys_kern_vfs_bio_c_2c248cd490d7

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/dragonflybsd`. This group contains one file, read completely: `sources/os/bsd/dragonflybsd/sys/kern/vfs_bio.c` (4,659 lines).

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_bio.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_bio.c

## Role
DragonFlyBSD kernel buffer I/O implementation for the coherent VM object and buffer cache scheme. It owns buffer header initialization, per-CPU clean/dirty/empty queues, `bread`/`bwrite` style APIs, delayed-write accounting, buffer daemon flushing, vnode strategy dispatch, BIO completion, VM page busy/clean/release transitions, KVABIO mapping synchronization, nested BIO fan-out, and DDB buffer inspection.

## Main Structures And State
- Buffer queue model: `BQUEUE_NONE`, `BQUEUE_LOCKED`, `BQUEUE_CLEAN`, `BQUEUE_DIRTY`, `BQUEUE_DIRTY_HW`, `BQUEUE_EMPTY` are per-CPU `TAILQ`s protected by `struct bufpcpu.spin` (`lines 69-95`).
- Global accounting: `bufspace`, `maxbufspace`, `lobufspace`, `hibufspace`, dirty KVA/buffer counters, running I/O counters, daemon request flags, wake ring, debug knobs, and `bufcache_bw` are exposed or controlled through `vfs.*` sysctls (`lines 128-212`).
- `bogus_page` is a VM page substitute used during partial reads so already-valid or dirty page data is not overwritten by gap-filling I/O (`lines 115-122`, `lines 3901-3994`).
- Embedded BIO layering is initialized by `initbufbio()`, reset by `reinitbufbio()`, and extended by `push_bio()`/`pop_bio()` to cache or add translation layers (`lines 719-811`).

## Initialization
- `bufinit()` initializes all per-CPU queues, zeroes every `struct buf`, assigns KVA reservations from `buffer_map`, initializes BIO/xio/dependency state, and distributes empty buffers round-robin across CPUs (`lines 607-689`).
- It computes buffer-space and dirty/running I/O watermarks, initializes dirty counters, and allocates/wires the global `bogus_page` (`lines 652-710`).
- Kernel threads `bufdaemon` and `bufdaemon_hw` are registered by `SYSINIT` and share `buf_daemon1()` with separate normal and heavyweight dirty queues (`lines 2212-2316`).

## Read/Write Entry Points
- `breadcb()` gets a buffer and either dispatches async read I/O with a caller callback or invokes the callback synchronously for cache hits (`lines 858-888`).
- `breadnx()` handles the primary read plus read-ahead. It avoids read-ahead I/O if `inmem()` says data is already present, uses KVABIO for read-ahead buffers, and waits only for the primary read (`lines 899-945`).
- `bwrite()` and `bawrite()` set write command state, mark buffers cache-valid, busy backing VM pages, account running bytes, and dispatch through `vn_strategy()`, with `bwrite()` waiting synchronously (`lines 963-1047`).
- `bdwrite()` marks delayed writes, precomputes the physical translation via `VOP_BMAP()`, cleans VM pages so pageout sees them as handled by the buffer cache, and requeues without issuing immediate I/O because softdeps can depend on that behavior (`lines 1061-1116`).
- `buwrite()` is a tmpfs-oriented fake write path that marks VM pages as needing commit and leaves the buffer clean unless it must fall back to `bdwrite()` (`lines 1126-1149`).

## Dirty And Running I/O Control
- `bdirty()`, `bheavy()`, `bundirty()`, and `bsetrunningbufspace()` maintain delayed-write state, heavyweight dirty accounting, dirty byte/count counters, and running I/O counters (`lines 1163-1258`).
- `bd_heatup()`, `bd_speedup()`, `bd_wait()`, and `bd_signal()` implement hysteresis and wakeup behavior for dirty/running space pressure using low/high dirty watermarks and a wake ring (`lines 390-521`).
- `waitrunningbufspace()` throttles submitters when running I/O exceeds the configured fraction of `hirunningspace` and also preserves fairness if another thread is already waiting (`lines 323-340`).

## Buffer Release And Reuse
- `brelse()` is the full release/destruction path. It handles `B_NOCACHE`, invalid/error buffers, delayed-write cleanup, low-memory `B_RELBUF`, VMIO rundown, bogus-page restoration, backing-page invalidation, vnode disassociation, queue placement, and wakeups (`lines 1268-1647`).
- `bqrelse()` is a lighter release path for buffers expected to be reused soon; it requeues locked, dirty, and clean buffers, but delegates to `brelse()` during severe paging pressure (`lines 1649-1728`).
- `bqhold()`/`bqdrop()` add a lightweight reuse-prevention reference, mainly for unlocked `uiomove()` windows and lookup races (`lines 1735-1758`).
- `vfs_vmio_release()` unwires backing pages, updates activity placement, optionally frees/caches pages for direct I/O, non-metadata, TTC, or paging pressure, removes KVA mappings without immediate TLB invalidation, adjusts `bufspace`, and drops vnode association (`lines 1761-1862`).

## Allocation, Lookup, And Cache Coherency
- `getnewbuf()` scans local then remote CPU empty/clean queues, ages clean buffers once before reuse, handles dependency deallocation, disassociates vnode/VM state, shrinks buffers, applies heavyweight flags, and sleeps on either buffer-count or buffer-space pressure when no reusable header exists (`lines 1884-2198`).
- `flushbufqueues()` uses a marker buffer to scan per-CPU dirty queues fairly, skips locked buffers, frees invalid dirty buffers, respects dependency deferral/checkwrite rules, and otherwise launches `cluster_awrite()` with `B_AGE` and KVABIO (`lines 2335-2478`).
- `inmem()` checks both the buffer cache and backing VM object page validity to decide whether I/O is needed (`lines 2489-2547`).
- `findblk()` looks up vnode/offset buffers in the vnode RB tree under `v_token`, uses `b_refs` to prevent reuse while locking, supports nonblocking/test/ref modes, and synchronizes KVA mappings if the caller does not opt into KVABIO (`lines 2555-2639`).
- `getcacheblk()` returns only fully cached non-`B_RAM` buffers, using either `getblk()` to instantiate from VM backing pages or `findblk()` for existing buffers (`lines 2641-2720`).
- `getblk()` is the central buffer acquisition routine. It resolves cache hits, lock races, size mismatches, dirty/dependency writeback, invalid cached translations, new buffer creation, vnode association, VMIO setup, `allocbuf()` growth, and final KVABIO synchronization (`lines 2728-2988`).
- `allocbuf()` grows or shrinks VMIO buffers by wiring/unwiring VM object pages, allocating missing pages through `bio_page_alloc()`, testing page validity to maintain `B_CACHE`, updating KVA mappings, and maintaining `bufspace`/dirty byte accounting (`lines 3029-3237`).

## BIO Dispatch And Completion
- `biowait()`/`biowait_timeout()` wait on `BIO_DONE`, clear sync/done bits, and translate `B_EINTR`/`B_ERROR` into caller-visible errors (`lines 3251-3307`).
- `bio_start_transaction()` attaches a `bio_track` and enters disk scheduling for callers that bypass normal vnode/device layers (`lines 3313-3331`).
- `vn_strategy()` marks `B_IOISSUED`, optionally intercepts page-aligned reads through swapcache, synchronizes KVABIO for vnodes that do not support it, attaches read/write tracking, enters dsched, and calls `vop_strategy()` (`lines 3348-3395`).
- `vn_cache_strategy()` diverts suitable page-aligned reads to `swap_pager_strategy()` when all backing pages are swap-cached, using a pushed BIO layer and a callback that clears the synthetic offset before resuming normal completion (`lines 3403-3506`).
- `bpdone()` finalizes I/O after all BIO layers are complete: it handles write redirty/undirty, softdep completion, `B_CACHE` updates, page valid/clean state, bogus-page restoration, VM paging-in-progress wakeups, and final release/requeue for async completions (`lines 3515-3715`).
- `biodone()` walks BIO layers backward, releases tracking refs, invokes layer callbacks, and calls `bpdone()` when the chain is exhausted; `biodone_sync()` completes synchronous BIOs without releasing the locked buffer (`lines 3720-3784`).

## VM Page And KVA Handling
- `vfs_busy_pages()` busies all VMIO pages before strategy dispatch, starts object paging accounting, write-protects pages for writes, cleans dirty ranges, replaces fully valid read pages with `bogus_page`, protects invalid read pages, updates KVA mappings if bogus pages were substituted, and accounts process block I/O (`lines 3859-4011`).
- `vfs_unbusy_pages()` is the incomplete-I/O cleanup path, restoring bogus pages, finishing page I/O, waking pages, and restoring KVA mappings (`lines 3799-3852`).
- `vfs_clean_pages()` and `vfs_clean_one_page()` mark buffer-covered page ranges valid and clean, fold VM dirty bits into `b_dirtyoff/b_dirtyend`, clear stale NFS commit state when mapped writes overlap, and avoid over-clearing partial-page dirty state (`lines 4018-4147`).
- `vfs_bio_clrbuf()` zero-fills invalid DEV_BSIZE regions in VMIO buffers, optimizes the common one-page case, marks valid bits, clears error/invalid flags, and synchronizes current CPU access via `bkvasync()` (`lines 4197-4251`).
- `bio_page_alloc()` allocates VM pages for buffers with CPU rotation, normal allocation first, controlled use of system reserves, tmpfs-specific reserve avoidance, deficit signaling, short waits, and rate-limited low-memory warnings (`lines 4264-4344`).
- `bkvareset()`, `bkvasync()`, and `bkvasync_all()` implement DragonFly's KVABIO contract: mappings may be lazily invalidated per CPU for KVABIO-aware consumers, while non-KVABIO consumers require full TLB synchronization before `B_KVABIO` is cleared (`lines 4358-4417`).

## Nested I/O And Diagnostics
- `scan_all_buffers()` iterates the global `buf[]` array and aggregates callback results, returning early on negative callback status (`lines 4424-4438`).
- `nestiobuf_*()` manages master BIO fan-out into sub-buffers: initialization holds a placeholder count, `nestiobuf_add()` wires sub-buffer callbacks and slices data, `nestiobuf_done()` atomically accumulates completion/error state, and `nestiobuf_start()` releases the placeholder and completes the master BIO when the last child finishes (`lines 4445-4588`).
- `buf_cmd_name()` maps buffer command enums to human-readable names (`lines 4591-4619`).
- Under `DDB`, `show buffer <addr>` prints flags, command, error, sizing, data pointer, disk/physical BIO offsets, and VM page object/index/physical address tuples (`lines 4624-4658`).

## Concurrency And Correctness Notes
- Queue membership is protected by per-CPU spinlocks, but buffer contents/state require `BUF_LOCK`; many paths explicitly revalidate queue index, vnode, offset, and `b_refs` after locking.
- Dirty state is deliberately cleared after successful write completion, not before dispatch, so filesystem checks and softdep/HAMMER/HAMMER2 interlocks can still observe pending dirty buffers during I/O.
- Partial reads avoid overwriting valid or potentially dirty VM page data by substituting `bogus_page`; completion/release paths must restore original object pages and KVA mappings.
- Low-memory behavior is distributed across allocation, release, and daemon flushing: `bio_page_alloc()` avoids reclaim recursion, while `brelse()`/`bqrelse()` and `getnewbuf()` return pages and apply backpressure.
- KVABIO is a performance-sensitive contract. Callers that do not explicitly support it must force `bkvasync_all()` before touching `b_data` or dispatching to a vnode/device that lacks `VKVABIO`.

## Research Notes
The file is a central integration point for VFS, VM, block strategy, swapcache, soft dependencies, disk scheduling, and debug tooling. Changes here have broad correctness risk around page dirty/valid bits, buffer queue placement, vnode hash membership, async writeback progress, and TLB synchronization.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/kern/vfs_bio.c -->