# Research: subset-b-007127

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/page.c -->
# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/page.c

## Purpose
Implements the page-cache mechanics for the GlusterFS `performance/read-ahead` translator. It manages sorted per-fd read-ahead pages, asynchronous page faults, wait queues for user reads blocked on in-flight pages, page fill/unwind aggregation, stale/poisoned invalidation, and fd-cache destruction.

## Important APIs, Types, And Functions
The file operates on `ra_file_t`, `ra_page_t`, `ra_waitq_t`, and `ra_local_t` from `read-ahead.h`. `ra_page_get()` and `ra_page_create()` locate or insert page records at `gf_floor(offset, page_size)`. `ra_wait_on_page()` attaches a frame to a page wait queue and increments the frame-local wait count. `ra_page_fault()` copies the user frame, allocates a local, refs the fd, and winds a child `readv` for one page. `ra_fault_cbk()` stores the returned iovecs/iobref in the page or propagates errors to waiters. `ra_frame_fill()`, `ra_frame_return()`, and `ra_frame_unwind()` assemble page fragments into the user `readv` reply. `ra_page_wakeup()`, `ra_page_error()`, `ra_page_purge()`, and `ra_file_destroy()` are the completion and teardown primitives.

## Control Flow
Callers create or find pages under the file lock, then either fill immediately from a ready page or wait on a pending page. A fault frame reads a full page from the child translator. On callback, the code verifies the fd context, handles pages removed or marked stale, marks dirty+poisoned read-ahead pages as canceled, copies successful data into the page, and wakes all queued frames. Each waiting frame receives the relevant subrange via `iov_subset()` and only unwinds once `wait_count` reaches zero. Stale pages are retried if the in-flight read completed after invalidation.

## State And Persistence
All state is in memory and scoped to an open fd. `ra_page_t` stores offset, size, copied vectors, iobref, readiness, dirty/stale/poisoned flags, and waiters. `ra_file_t` owns the page list and file lock. Data is not durable; it is a client-side cache that must be invalidated on writes, truncates, discard, zerofill, and release.

## Dependencies And Integration Points
Depends on Gluster call frames, STACK_WIND/UNWIND, fd contexts, `iobref`, iovec helpers, memory accounting types from `read-ahead-mem-types.h`, and message IDs from `read-ahead-messages.h`. It is called by `read-ahead.c` for user reads, speculative reads, mutation invalidation, and fd release.

## Risks
Correctness depends on careful lock ordering and wait-count accounting. `ra_frame_unwind()` assumes the fd context still exists to supply `file->stbuf`; release races or missing fd context paths are high-risk. The code copies page iovecs but relies on iobref lifetimes to keep backing buffers valid. Dirty/poisoned handling prevents stale speculative data from being served, but mistakes around stale retry can either drop data or loop. Memory failures while filling a multi-page read turn the whole request into an error.

## Test Signals
Useful tests include sequential reads spanning several pages, concurrent readers waiting on the same page, OOM/error injection in `copy_frame`, `iov_dup`, `iobref_new`, and `iov_subset`, writes racing with in-flight speculative reads, fd release with pending pages, and short final-page reads. Statedump should show page offsets and waiters disappearing after wakeup or purge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead-mem-types.h

## Purpose
Defines memory-accounting IDs for allocations made by the read-ahead translator.

## Important APIs, Types, And Functions
`enum gf_ra_mem_types_` starts at `gf_common_mt_end + 1` and names allocation classes for `ra_file_t`, `ra_conf_t`, `ra_page_t`, `ra_waitq_t`, `ra_fill_t`, and iovec arrays, ending with `gf_ra_mt_end`.

## Control Flow
`read-ahead.c` passes `gf_ra_mt_end` to `xlator_mem_acct_init()`. Allocation sites in `page.c` and `read-ahead.c` use the individual enum values with `GF_CALLOC`.

## State And Persistence
No runtime state is stored here; the enum is part of Gluster's in-process memory accounting namespace.

## Dependencies And Integration Points
Includes `glusterfs/mem-types.h` and is included by `read-ahead.h`, making these IDs available to all read-ahead implementation files.

## Risks
IDs must remain unique relative to common memory types and should be extended only before `gf_ra_mt_end`. Mislabeling allocations mainly affects diagnostics and leak attribution.

## Test Signals
Translator initialization should call memory accounting successfully. Leak/statedump tooling should attribute read-ahead file, page, wait queue, fill, and iovec allocations to these IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead-messages.h -->
# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead-messages.h

## Purpose
Declares stable log message IDs for the read-ahead translator.

## Important APIs, Types, And Functions
The `GLFS_MSGID(READ_AHEAD, ...)` block defines IDs for child misconfiguration, volume misconfiguration, no memory, missing fd context, undestroyed file state, and null translator config.

## Control Flow
Implementation files pass these IDs to `gf_msg()` and related logging calls during init, fd-context failures, memory failures, and fini diagnostics.

## State And Persistence
No runtime state is stored. The IDs are an operational compatibility surface; comments explicitly require appending new IDs rather than removing or reusing old ones.

## Dependencies And Integration Points
Includes `glusterfs/glfs-message-id.h` and relies on `READ_AHEAD` being a registered component name.

## Risks
Removing, reordering, or reusing IDs can break log parsers and downstream diagnostics. Adding IDs under the wrong component would misclassify logs.

## Test Signals
Builds should confirm `READ_AHEAD` is known to the message-id system. Runtime misconfiguration and missing-fd-context paths should emit the expected component IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead.c -->
# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead.c

## Purpose
Implements the `performance/read-ahead` xlator. It detects sequential read patterns, serves reads from a per-fd page cache, speculatively issues child `readv` operations, invalidates cached pages on file mutations, supports statedump, and exposes volume options for page sizing, page count, atime behavior, and pass-through.

## Important APIs, Types, And Functions
Public fops are `ra_open`, `ra_create`, `ra_readv`, `ra_writev`, `ra_flush`, `ra_fsync`, `ra_truncate`, `ra_ftruncate`, `ra_fstat`, `ra_discard`, and `ra_zerofill`. `ra_open_cbk()` and `ra_create_cbk()` allocate `ra_file_t` fd contexts, disabling caching for `O_DIRECT` and write-only opens. `dispatch_requests()` handles user read cache hits, misses, and waits. `read_ahead()` schedules speculative dirty page faults. `flush_region()` invalidates ready pages or marks pending pages stale/poisoned. Init/reconfigure/fini manage `ra_conf_t`, local frame pools, and options.

## Control Flow
Open/create attaches a read-ahead file context to the fd and links it into the translator config. `ra_readv()` bypasses disabled fds, compares the request offset against the expected sequential offset, resets prefetch depth on random reads, allocates `ra_local_t`, dispatches required pages, flushes old pages before the current offset, schedules future read-ahead pages, updates the next expected offset, and returns when all page waiters complete. Mutating fops walk all fds on the inode and invalidate cached pages before winding the child operation. `fstat` invalidates cached pages when `force-atime-update` is enabled.

## State And Persistence
`ra_conf_t` stores configured page size/count, atime behavior, the global list of open file contexts, and a config lock. Each `ra_file_t` tracks expected sequential offset, dynamic prefetch page count, cached pages, last stat buffer, fd pointer, disabled flag, and lock. State lives only in memory and is discarded on fd release or translator fini.

## Dependencies And Integration Points
Uses the Gluster xlator API, fd/inode contexts, frame-local memory pools, statedump hooks, child `readv`/mutation fops, iovec and iobref helpers, option parsing macros, and the page helpers in `page.c`. It integrates with other performance translators by respecting `pass-through` and by optionally forcing atime updates through a tiny child read.

## Risks
The implementation intentionally flushes broad ranges, often the whole cached fd, which is safe but can reduce benefit. Sequential-detection state is updated without a dedicated lock in `ra_readv`, so concurrent reads on the same fd can disrupt prefetch heuristics. `ra_create_cbk()` does not reduce page count to one for non-disabled created files while `ra_open_cbk()` does; that asymmetry may affect initial prefetch behavior. The atime workaround performs an extra child read that can interact poorly with other cache translators. Mutation invalidation must cover every fop that can change file data.

## Test Signals
Exercise sequential, random, and concurrent reads; O_DIRECT and write-only opens; writes/truncates/discard/zerofill racing with cached and in-flight pages; `force-atime-update`; option reconfigure for page size/count and pass-through; fd release/fini with cached pages; and statedump output. Performance signals should show fewer child reads for sequential reads and no stale data after mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead.h -->
# sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead.h

## Purpose
Declares the read-ahead translator's private structures, helper prototypes, and lock wrappers shared by `read-ahead.c` and `page.c`.

## Important APIs, Types, And Functions
`ra_waitq` stores blocked frames. `ra_fill` stores one returned page fragment for user unwind. `ra_local` tracks a user read's range, wait count, error state, pending fault metadata, fd, fill list, and mutex. `ra_page` stores cached page data and invalidation flags. `ra_file` stores per-fd cache state and sequential-read counters. `ra_conf` stores translator options and all open files. Prototypes expose page lookup/create/fault/wakeup/error/purge, frame fill/return, and file destroy helpers. Inline lock helpers wrap pthread mutexes.

## Control Flow
The header itself has no control flow, but it defines the contracts used by read dispatch: pages are protected by `ra_file_lock`, frame-local wait counts by `ra_local_lock`, and the global file list by `ra_conf_lock`.

## State And Persistence
All structures are transient in-memory state. The shape of `ra_page` and `ra_file` determines cache lifetime, invalidation semantics, and statedump visibility.

## Dependencies And Integration Points
Includes Gluster logging, dict, xlator APIs, and read-ahead memory types. It is the internal ABI between the page-cache implementation and the xlator fop layer.

## Risks
The structures expose raw linked-list pointers and manual lock discipline; misuse can corrupt lists or race with callbacks. `ra_file.refcount` is declared but not visibly central in the current implementation, so lifetime is mainly governed by fd contexts and release.

## Test Signals
Compile-time tests should catch signature drift between `page.c` and `read-ahead.c`. Runtime lock, leak, and statedump diagnostics should validate that file/page/local objects are created and destroyed through these structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/read-ahead/src/read-ahead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/Makefile.am

## Purpose
Top-level Automake file for the `performance/readdir-ahead` translator directory.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src` and an empty `CLEANFILES`.

## Control Flow
Automake descends into `src`, where the actual module build is defined.

## State And Persistence
No runtime state. It affects source-tree build traversal only.

## Dependencies And Integration Points
Integrated by the parent performance translator Makefile and GlusterFS build system.

## Risks
If `src` is omitted or renamed here, the translator library will not be built. No install artifacts are declared at this level.

## Test Signals
`make` from the parent should enter `readdir-ahead/src` and build `readdir-ahead.la`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/Makefile.am

## Purpose
Defines the build recipe for the `readdir-ahead` xlator module.

## Important APIs, Types, And Functions
Builds `readdir-ahead.la` into the performance xlator directory. Sources are `readdir-ahead.c`; private headers are `readdir-ahead.h`, `readdir-ahead-mem-types.h`, and `readdir-ahead-messages.h`. Links against `libglusterfs.la`.

## Control Flow
Automake compiles the single C source with Gluster and RPC/XDR include paths and module linker flags.

## State And Persistence
No runtime state. It controls installed module location under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/performance`.

## Dependencies And Integration Points
Depends on `GF_CPPFLAGS`, `GF_CFLAGS`, `GF_XLATOR_DEFAULT_LDFLAGS`, libglusterfs, and XDR headers.

## Risks
Missing headers from `noinst_HEADERS` would not be distributed to builds. Incorrect `xlatordir` would install the translator into the wrong category.

## Test Signals
Build output should produce a loadable `readdir-ahead.la` module with no unresolved libglusterfs symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead-mem-types.h

## Purpose
Defines memory-accounting IDs for the readdir-ahead translator.

## Important APIs, Types, And Functions
`enum gf_rda_mem_types_` names allocations for `rda_local`, fd context, private config, inode context, and the end marker.

## Control Flow
`readdir-ahead.c` calls `xlator_mem_acct_init(this, gf_rda_mt_end)` and uses these IDs for `GF_CALLOC` allocations.

## State And Persistence
No persistent state; the enum labels runtime allocations for diagnostics.

## Dependencies And Integration Points
Includes `glusterfs/mem-types.h` and is included by both `readdir-ahead.h` and `readdir-ahead.c`.

## Risks
Forgetting to add new allocation classes can obscure leak reports. Reordering IDs can confuse long-running diagnostic expectations.

## Test Signals
Memory-accounting init should succeed, and leak/statedump tooling should attribute readdir-ahead locals, fd contexts, private config, and inode contexts correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead-messages.h -->
# sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead-messages.h

## Purpose
Declares stable log message IDs for the readdir-ahead translator.

## Important APIs, Types, And Functions
`GLFS_MSGID(READDIR_AHEAD, ...)` defines IDs for child and volume misconfiguration, allocation failure, directory release with a pending stub, out-of-sequence prefetch, and dictionary operation failure.

## Control Flow
The implementation logs these IDs during init, prefetch callback validation, release, and memory/dict error paths.

## State And Persistence
No runtime state. IDs must remain append-only to preserve log compatibility.

## Dependencies And Integration Points
Includes `glusterfs/glfs-message-id.h` and relies on the `READDIR_AHEAD` component.

## Risks
Changing message order or deleting IDs breaks stable diagnostics. Missing IDs can force generic logs for important corruption paths such as out-of-sequence directory preload.

## Test Signals
Misconfiguration, OOM injection, and forced out-of-sequence prefetch tests should emit these IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead.c -->
# sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead.c

## Purpose
Implements `performance/readdir-ahead`, which converts small sequential `readdirp` requests into larger child `readdirp` prefetches. It buffers directory entries per fd, serves sequential callers from the buffer, disables itself on non-sequential access, maintains a global cache limit, and refreshes or invalidates entry `iatt` data when file metadata changes during prefetch.

## Important APIs, Types, And Functions
Main fops are `rda_opendir`, `rda_readdirp`, mutation fops for data and metadata writes, and cbks `rda_releasedir`/`rda_forget`. `get_rda_fd_ctx()` creates `rda_fd_ctx` with state flags such as `RDA_FD_NEW`, `RUNNING`, `EOD`, `ERROR`, `BYPASS`, and `PLUGGED`. `rda_fill_fd()` and `rda_fill_fd_cbk()` drive internal prefetch. `__rda_fill_readdirp()` and `__rda_serve_readdirp()` move entries from cache to the caller. `rda_inode_ctx_update_iatts()` maintains per-inode stat snapshots and generation counters. `RDA_COMMON_MODIFICATION_FOP` wraps mutation calls to update inode stat state after success.

## Control Flow
`opendir` stores md-cache xdata keys and starts a filler. `rda_readdirp()` checks fd context state under lock; if the offset is unexpected or another user stub is pending, it marks bypass and sends the request to the child. Otherwise it serves from cache when enough data, EOD, or error state exists; if not, it stores a single pending stub and ensures the filler is running. The filler issues large child `readdirp` calls at `next_offset`, appends returned entries to `ctx->entries`, updates cache accounting, handles EOD/error, wakes a pending stub when possible, and continues until bypass, EOD, error, or cache limit stops it.

## State And Persistence
Per-fd state includes current served offset, next prefetch offset, cached byte size, state flags, pending stub, fill frame, xdata keys, writes-during-prefetch dictionary, atomic prefetch counter, and cached dirent list. Translator-private state stores request size, watermarks, cache limit, global cache size, and `parallel-readdir`. Per-inode context stores the latest trusted `iatt` and a generation counter. All state is in memory and freed on `releasedir` or inode forget.

## Dependencies And Integration Points
Uses Gluster call stubs, fd/inode contexts, gf_dirent lists, dict APIs, atomic counters, child `readdirp`, mutation fops, md-cache xdata propagation, and option parsing. It is sensitive to write-behind because write-behind may return cached write responses with invalid or delayed `iatt`, so this translator invalidates stat snapshots when needed.

## Risks
Only one pending user stub is supported; concurrent or out-of-order reads force bypass. Cache-limit handling stops prefetch globally, which can affect unrelated directories. `parse` and generation logic for writes during prefetch is subtle: missing an invalidation can expose stale `d_stat`, while over-invalidation loses metadata-cache value. `rda_releasedir()` logs but does not unwind a pending stub, so release with in-flight user request is a serious lifecycle anomaly. `parallel-readdir` is parsed but not directly used in this file, implying cross-translator behavior or dead configuration.

## Test Signals
Test sequential `ls`-style reads, offset resets to zero after EOD, non-sequential offsets, concurrent callers, cache high/low watermark transitions, global cache-limit stop, child `ENOENT`/error propagation, md-cache xdata reuse, writes/truncates/xattr/setattr during active prefetch, and releasedir while fill is active. Check cache-size accounting returns to zero after release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead.h -->
# sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead.h

## Purpose
Declares internal flags, helper macros, and state structures for `performance/readdir-ahead`.

## Important APIs, Types, And Functions
State flags define fd lifecycle and bypass behavior. `RDA_COMMON_MODIFICATION_FOP` allocates a local, refs the inode and xdata, captures the inode generation, and winds a child mutation fop. `RDA_STACK_UNWIND` unwinds and cleans `rda_local`. `rda_fd_ctx` stores directory prefetch state and cached entries. `rda_local` carries per-call state for prefetch and mutation callbacks. `rda_priv` stores option values and global cache size. `rda_inode_ctx_t` stores cached `iatt` plus generation.

## Control Flow
The macros shape most mutation callback control flow in `readdir-ahead.c`: every wrapped mutation captures pre-operation generation and updates stat cache only if the callback data is still valid for that generation.

## State And Persistence
All structures are in-memory translator state. Fd context lifetime follows directory fd lifetime; inode context lifetime follows inode forget.

## Dependencies And Integration Points
Requires Gluster locks, atomics, dirent lists, dicts, fds, inodes, and call stubs through included implementation context. It is the contract between the prefetch path and the metadata invalidation path.

## Risks
The macros assume `__rda_inode_ctx_get()` succeeds; if allocation fails, dereferencing `ctx_p` would be unsafe. The state flags are bit masks manipulated under `ctx->lock`; missing locking can corrupt bypass/EOD/run decisions.

## Test Signals
Compile tests should catch macro signature mismatch for all wrapped fops. Runtime mutation tests should show locals cleaned, xdata unrefed, and generation counters preventing stale stat updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/write-behind/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/write-behind/Makefile.am

## Purpose
Top-level Automake file for the `performance/write-behind` translator directory.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src` and empty `CLEANFILES`.

## Control Flow
The build system descends into `src` to compile the actual module.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Integrated by parent performance translator build files.

## Risks
If `src` is not listed, write-behind will not be built or installed.

## Test Signals
Parent builds should enter `write-behind/src` and produce the xlator module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/write-behind/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/Makefile.am

## Purpose
Defines the build recipe for the `write-behind` xlator module.

## Important APIs, Types, And Functions
Builds `write-behind.la` into the performance xlator directory from `write-behind.c`, links `libglusterfs.la`, and declares `write-behind-mem-types.h` and `write-behind-messages.h` as private headers.

## Control Flow
Automake compiles the module with Gluster and RPC/XDR include paths and module linker flags.

## State And Persistence
No runtime state. Install path is `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/performance`.

## Dependencies And Integration Points
Depends on `GF_CPPFLAGS`, `GF_CFLAGS`, `GF_XLATOR_DEFAULT_LDFLAGS`, and libglusterfs.

## Risks
Missing source/header entries can break distribution builds. Wrong install directory would prevent graph loading by category/name.

## Test Signals
Build should produce `write-behind.la` with no unresolved Gluster symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/write-behind-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/write-behind-mem-types.h

## Purpose
Defines memory-accounting IDs for the write-behind translator.

## Important APIs, Types, And Functions
`enum gf_wb_mem_types_` names allocation classes for legacy `wb_file_t`, `wb_request_t`, iovec arrays, `wb_conf_t`, `wb_inode_t`, and the end marker.

## Control Flow
`write-behind.c` initializes accounting with `gf_wb_mt_end` and uses these IDs for request, inode, and config allocations.

## State And Persistence
No runtime state; labels allocations for diagnostics.

## Dependencies And Integration Points
Includes `glusterfs/mem-types.h` and is consumed by `write-behind.c`.

## Risks
`gf_wb_mt_wb_file_t` appears retained though the current code centers on `wb_inode_t`; stale allocation labels can confuse readers but preserve compatibility.

## Test Signals
Memory-accounting initialization and leak reports should show write-behind request, inode, and config allocation classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/write-behind-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/write-behind-messages.h -->
# sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/write-behind-messages.h

## Purpose
Declares stable log message IDs for the write-behind translator.

## Important APIs, Types, And Functions
`GLFS_MSGID(WRITE_BEHIND, ...)` defines IDs for size/config errors, init failure, invalid argument, memory failure, missing size, volume misconfiguration, unavailable resources, and pass-through warnings.

## Control Flow
`write-behind.c` emits these IDs during init/reconfigure, request refcount anomalies, iobref failures, and memory accounting failures.

## State And Persistence
No runtime state. IDs are stable operational identifiers and should be append-only.

## Dependencies And Integration Points
Includes `glusterfs/glfs-message-id.h` and uses the `WRITE_BEHIND` component.

## Risks
Changing IDs disrupts log tooling. Missing message IDs for queue corruption or sync errors would make field diagnosis harder.

## Test Signals
Invalid `aggregate-size`/`cache-size`, pass-through reconfigure, OOM injection, and refcount error paths should log under these IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/write-behind-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/write-behind.c -->
# sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/write-behind.c

## Purpose
Implements `performance/write-behind`, a client-side write buffering xlator. It can acknowledge non-sync writes before backend completion, aggregate sequential small writes, preserve ordering for overlapping or strict-order dependencies, route barriers such as flush/fsync through the queue, retry failed backend syncs under configured policy, and hide stale `readdirp` stat data while cached writes are outstanding.

## Important APIs, Types, And Functions
`wb_inode_t` owns per-inode queues: `todo`, `liability`, `temptation`, `wip`, `all`, plus write window, transit bytes, generation, file size, invalidation state, and lock. `wb_request_t` wraps a call stub with ordering range, write size, fd/lkowner/pid, generation, refcount, and flags for append, tempted, lied, fulfilled, and go. Core helpers include `wb_enqueue_common()`, `wb_requests_conflict()`, `__wb_pick_winds()`, `__wb_pick_unwinds()`, `wb_fulfill()`, `wb_fulfill_cbk()`, `wb_process_queue()`, and `__wb_collapse_small_writes()`. Fops wrap writes, reads, flush, fsync, stat/fstat, truncate/ftruncate, setattr/fsetattr, lookup, readdirp, link, fallocate, discard, zerofill, and rename.

## Control Flow
Writes create per-inode context as needed. Sync, dsync, and optionally O_DIRECT writes are enqueued as normal tasks; other writes enter `temptation` and may be unwound early when window capacity permits. `wb_process_queue()` repeatedly preprocesses aggregation candidates, picks safe child winds after checking liability and WIP conflicts, unwinds newly lied writes, and sends selected liabilities to backend writev fulfillment. Fulfillment aggregates adjacent writes sharing fd/lkowner/offset within vector and size limits. Backend callbacks mark writes fulfilled, retry or fail on errors, handle short writes by adjusting request offsets/vectors, and reprocess the queue. Flush/fsync/read/stat-like fops enqueue behind dependent cached writes to preserve consistency.

## State And Persistence
State is in-memory per inode and exists until inode forget. Liability generation captures causal dependencies at enqueue time. Window accounting tracks bytes acknowledged but not yet safely fulfilled. File size is updated optimistically on writes/truncates and refreshed from lookup/truncate callbacks. Readdirp invalidation state tracks directories with active readdirp sessions and child inodes whose cached write completion could make returned `d_stat` stale.

## Dependencies And Integration Points
Uses Gluster call stubs, xlator fops, inode contexts, fd refs, iobuf/iobref, iovec helpers, locks, atomics, statedump, option parsing, and default callback helpers. It coordinates with directory metadata consumers by clearing `readdirp` entry inode/stat for regular files with outstanding liabilities or invalidation flags.

## Risks
The queue state machine is complex: refcounts, list membership, and generation checks must stay consistent across early unwind, backend retry, short write, and failure. Flush/fsync semantics are configuration-sensitive, especially `flush-behind` and `resync-failed-syncs-after-fsync`. Aggregation mutates request iovecs and iobrefs; allocation or merge failures must not leak or double-unwind. Append and O_DIRECT handling depend on flags and `strict-O_DIRECT`. The `wb_zerofill()` unwind path falls through to `noqueue` after an ENOMEM unwind, which is a code-shape risk for double handling. Stale `readdirp` stat mitigation relies on active-directory tracking and can miss cases if inode contexts are absent.

## Test Signals
Test buffered writes with early success, overlapping writes, non-overlapping writes with and without strict ordering, append writes, sync/dsync/O_DIRECT writes, flush/fsync barriers, flush-behind, backend write failure and retry policy, short writes, aggregation boundaries, file size after write/truncate/lookup, readdirp while cached writes are outstanding, inode forget with empty queues, and statedump of queue/window state. Fault injection for iobuf/iobref/frame allocation is important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/write-behind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/playground/Makefile.am

## Purpose
Top-level Automake file for playground translators.

## Important APIs, Types, And Functions
Declares `SUBDIRS = template` and empty `CLEANFILES`.

## Control Flow
The build descends only into `template` from this directory.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Integrated by the broader xlator build. The sibling `rot-13` directory has its own Makefile but is not listed here.

## Risks
Because `rot-13` is omitted from `SUBDIRS`, a normal recursive build from `playground` will not build that sample unless another parent includes it separately.

## Test Signals
Automake traversal should build `template` only from this level; verify whether that exclusion is intended for `rot-13`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/rot-13/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/playground/rot-13/Makefile.am

## Purpose
Top-level Automake file for the sample `rot-13` translator.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src` and empty `CLEANFILES`.

## Control Flow
If this directory is reached by the build, Automake descends into `src`.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Depends on parent build files choosing to include `rot-13`.

## Risks
This file is inert if no parent lists `rot-13` in `SUBDIRS`.

## Test Signals
Direct build from this directory should enter `src` and build `rot-13.la`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/rot-13/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/rot-13/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/playground/rot-13/src/Makefile.am

## Purpose
Defines the build recipe for the sample ROT13 xlator.

## Important APIs, Types, And Functions
Builds `rot-13.la` from `rot-13.c`, installs under `xlator/encryption`, links `libglusterfs.la`, and declares `rot-13.h` as a private header.

## Control Flow
Automake compiles with Gluster and RPC/XDR include paths and xlator module linker flags.

## State And Persistence
No runtime state. The install path categorizes this sample as encryption rather than playground.

## Dependencies And Integration Points
Uses `GF_CPPFLAGS`, `GF_CFLAGS`, `GF_XLATOR_DEFAULT_LDFLAGS`, and libglusterfs.

## Risks
The install category differs from its source-tree playground location. Since the translator is sample-quality and not production-safe, accidental installation/loading is a risk if build traversal includes it.

## Test Signals
Direct module build should produce `rot-13.la`; packaging should verify whether installing this sample is desired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/rot-13/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/rot-13/src/rot-13.c -->
# sources/distributed-fs/glusterfs/xlators/playground/rot-13/src/rot-13.c

## Purpose
Implements a demonstration translator that applies ROT13 to write buffers before sending them to disk and applies ROT13 again to read buffers before returning to the caller. The file explicitly marks the translator as an example, not production code.

## Important APIs, Types, And Functions
`rot13()` transforms alphabetic bytes in place. `rot13_iovec()` applies it to each iovec. `rot13_readv()` winds child readv and `rot13_readv_cbk()` optionally decrypts returned vectors. `rot13_writev()` optionally encrypts user vectors before winding child writev. `init()` validates exactly one child, parses `encrypt-write` and `decrypt-read`, allocates `rot_13_private_t`, and sets defaults to enabled. `fini()` frees private state. The fop table exposes only readv and writev.

## Control Flow
Reads pass through to the child and are transformed in the callback immediately before unwind. Writes are transformed before the child sees the buffers. Init stores booleans from translator options, with errors for non-boolean values.

## State And Persistence
Persistent translator state is just two booleans in `rot_13_private_t`. Data persistence is external: if `encrypt-write` is enabled, bytes stored below this translator are ROT13-encoded.

## Dependencies And Integration Points
Uses Gluster xlator/frame APIs, logging, dict options, and the `rot-13.h` private struct. It requires one child and supports no cbks beyond the default empty struct.

## Risks
It mutates input and output iovec memory in place, which can surprise callers or violate ownership expectations in real stacks. It has minimal validation, no memory accounting, no xlator_api object, and no handling for partial writes, checksums, metadata, direct I/O, or binary-safe encryption semantics. ROT13 is not encryption.

## Test Signals
A round-trip write/read of alphabetic text should return original data when both options are on, stored data should be transformed under the translator, and disabling either option should produce one-way transformed behavior. Binary and shared-buffer tests would expose the in-place mutation risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/rot-13/src/rot-13.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/rot-13/src/rot-13.h -->
# sources/distributed-fs/glusterfs/xlators/playground/rot-13/src/rot-13.h

## Purpose
Declares private configuration state for the sample ROT13 translator.

## Important APIs, Types, And Functions
`rot_13_private_t` contains `encrypt_write` and `decrypt_read` booleans.

## Control Flow
`rot-13.c` reads these flags in read and write paths and initializes them from options.

## State And Persistence
The struct is per-translator in-memory state. It determines whether persisted child data is transformed on writes and whether reads are transformed back.

## Dependencies And Integration Points
Relies on `gf_boolean_t` being available from included Gluster headers in the C file context.

## Risks
The header does not include the Gluster type definition itself, so standalone inclusion without prior Gluster headers would fail.

## Test Signals
Builds including `rot-13.h` after Gluster headers should compile; option toggles should change the two flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/rot-13/src/rot-13.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/template/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/playground/template/Makefile.am

## Purpose
Top-level Automake file for the playground template translator.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src`.

## Control Flow
Automake descends into `src` to build the template module.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Integrated by `xlators/playground/Makefile.am`.

## Risks
No `CLEANFILES` is declared here; not an issue unless future generated files are added.

## Test Signals
Recursive build from playground should enter `template/src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/template/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/template/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/playground/template/src/Makefile.am

## Purpose
Defines the build recipe for the playground template xlator.

## Important APIs, Types, And Functions
Builds `template.la` from `template.c`, installs under `xlator/playground`, links `libglusterfs.la`, and declares `template.h` as a private header.

## Control Flow
Automake compiles the module using Gluster and RPC/XDR include paths.

## State And Persistence
No runtime state. It controls installed module location.

## Dependencies And Integration Points
Uses Gluster xlator module flags and libglusterfs.

## Risks
As a template, it is intentionally skeletal. Accidentally enabling it in a production graph would add no real fops.

## Test Signals
Build should produce a loadable `template.la`; loading it should exercise init and option parsing only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/template/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/template/src/template.c -->
# sources/distributed-fs/glusterfs/xlators/playground/template/src/template.c

## Purpose
Provides a maintained example skeleton for writing a GlusterFS translator. It demonstrates memory accounting, private option parsing, statedump/priv-to-dict hooks, metrics output, init/fini/reconfigure, notify forwarding, xlator API registration, and option metadata.

## Important APIs, Types, And Functions
`template_mem_acct_init()` initializes memory accounting. `template_init()` validates exactly one child and at least one parent, allocates `template_private_t`, and parses `dummy`. `template_reconfigure()` updates `dummy`. `template_fini()` frees private state. `template_priv()`, `template_priv_to_dict()`, and `template_dump_metrics()` expose private state to diagnostics. `template_notify()` forwards all events to `default_notify()`. `xlator_api` wires these hooks with empty fop/cbk tables and `template_options`.

## Control Flow
Module load calls memory accounting then init. Runtime events enter `template_notify()` and are forwarded. Statedump and metrics paths read `priv->dummy`. Reconfigure uses Gluster option macros to update the integer. Fini clears `this->private`.

## State And Persistence
Only `template_private_t.dummy` is stored in memory. No filesystem operations are intercepted because the fop table is empty.

## Dependencies And Integration Points
Uses Gluster xlator API, defaults, dict, logging, statedump, message IDs from `template.h`, and volume option metadata with experimental tags.

## Risks
The parent check rejects dangling volumes as an error, unlike some production translators that only warn. `template_priv_to_dict()` does not check for null private state. Empty fops mean the template is not functional unless extended.

## Test Signals
Loading with valid graph should set `dummy`; invalid graph should fail. Reconfigure should update `dummy`. Statedump, `priv_to_dict`, and metrics should report the same value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/template/src/template.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/template/src/template.h -->
# sources/distributed-fs/glusterfs/xlators/playground/template/src/template.h

## Purpose
Declares the private state, memory type IDs, and message IDs for the playground template translator.

## Important APIs, Types, And Functions
`template_private_t` contains a sample `dummy` field. `enum gf_template_mem_types_` defines the private allocation ID and end marker. `GLFS_MSGID(TEMPLATE, ...)` declares no-memory and no-graph message IDs.

## Control Flow
`template.c` uses these declarations during init, reconfigure, diagnostics, and memory accounting.

## State And Persistence
Only the in-memory `dummy` field is represented. No durable state is defined.

## Dependencies And Integration Points
Includes core Gluster headers, defaults, memory types, and message ID support. The comments explain how a real translator would split mem-types and messages into separate headers.

## Risks
Combining template, mem-type, and message declarations in one header is useful for an example but not the typical production layout. The `TEMPLATE` message component must exist in `glfs-message-id.h`.

## Test Signals
Compilation validates the message component and memory type usage. Statedump and metrics confirm `template_private_t` is populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/playground/template/src/template.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/protocol/Makefile.am

## Purpose
Top-level Automake file for protocol translators and authentication modules.

## Important APIs, Types, And Functions
Declares `SUBDIRS = auth client server`.

## Control Flow
Recursive builds descend into auth modules, protocol client, and protocol server directories.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Connects protocol components into the broader xlator build.

## Risks
Removing a subdir here excludes a core protocol component from builds.

## Test Signals
Parent build should visit auth, client, and server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/protocol/auth/Makefile.am

## Purpose
Top-level Automake file for protocol authentication modules.

## Important APIs, Types, And Functions
Declares `SUBDIRS = addr login`.

## Control Flow
Build descends into address-based and login-based auth modules.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Integrated by `xlators/protocol/Makefile.am`.

## Risks
Omitting either subdir removes an authentication backend from the build.

## Test Signals
Recursive build should produce both `addr.la` and `login.la`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/addr/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/protocol/auth/addr/Makefile.am

## Purpose
Top-level Automake file for the address-based auth module.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src`.

## Control Flow
Automake descends into `src` to build the module.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrated by the protocol auth build.

## Risks
If not traversed, address auth options would be documented but no module would be available.

## Test Signals
Build should enter `auth/addr/src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/addr/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/addr/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/protocol/auth/addr/src/Makefile.am

## Purpose
Defines the build recipe for the address-based authentication module.

## Important APIs, Types, And Functions
Builds `addr.la` into the Gluster auth module directory from `addr.c`, links `libglusterfs.la`, and includes server, RPC/XDR, and RPC library headers.

## Control Flow
Automake compiles the module with auth-module linker flags.

## State And Persistence
No runtime state. Install path is `$(libdir)/glusterfs/$(PACKAGE_VERSION)/auth`.

## Dependencies And Integration Points
Uses `authenticate.h` from the protocol server source tree and RPC transport types.

## Risks
Incorrect include paths would break the module's dependency on server authentication interfaces. Wrong `authdir` would prevent dynamic auth loading.

## Test Signals
Build should produce loadable `addr.la`; server auth loading should find it in the auth directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/addr/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/addr/src/addr.c -->
# sources/distributed-fs/glusterfs/xlators/protocol/auth/addr/src/addr.c

## Purpose
Implements address-based RPC authentication for protocol/server. It accepts or rejects clients based on configured allow/reject address patterns for the requested remote subvolume, optional subdir-specific rules, address family, and privileged-port policy.

## Important APIs, Types, And Functions
`gf_auth()` is the exported auth entry point. It reads `remote-subvolume`, `peer-info`, `subdir-mount`, `auth.addr.<subvol>.allow`, `auth.addr.<subvol>.reject`, legacy `auth.ip.<subvol>.allow`, and `rpc-auth-allow-insecure`. `parse_entries_and_compare()` handles either legacy comma-delimited address lists or subdir form `/dir(addr|addr),/other(addr)`. `compare_addr_and_update()` checks hostnames, CIDR/network strings, fnmatch patterns, and negated entries. `options[]` documents allow/reject options.

## Control Flow
`gf_auth()` starts as `AUTH_DONT_CARE`. It finds configured allow/reject lists, extracts the peer address from IPv4/IPv6/SDP or UNIX peer info, rejects unprivileged TCP ports unless insecure auth is allowed, applies reject rules first, and then allow rules. A matching reject returns `AUTH_REJECT`; a matching allow returns `AUTH_ACCEPT`; absent or nonmatching configuration leaves `AUTH_DONT_CARE`.

## State And Persistence
No persistent module state. All decisions are computed from input and config dictionaries per authentication call.

## Dependencies And Integration Points
Uses Gluster dict/data helpers, `authenticate.h`, `rpc-transport.h`, peer info, `gf_is_same_address()`, `gf_is_ip_in_net()`, `valid_host_name()`, `fnmatch()`, and socket address families. Loaded by the protocol server auth framework.

## Risks
Parsing mutates duplicated option strings with `strtok_r`; invalid subdir syntax can abort processing early. The comment notes that a negation flag is not reset per entry in `compare_addr_and_update()`, so a negated entry can affect later entries in the same call. `strrchr(peer_addr, ':')` is assumed to find a service separator for IP peers. Reject is evaluated before allow, which is safe but must be documented for operators.

## Test Signals
Cover IPv4, IPv6, UNIX sockets, privileged and unprivileged ports, `rpc-auth-allow-insecure`, wildcard/hostname/CIDR/fnmatch entries, negated entries, reject-before-allow, legacy `auth.ip.*.allow`, subdir-specific rules, malformed subdir entries, and missing peer info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/addr/src/addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/login/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/protocol/auth/login/Makefile.am

## Purpose
Top-level Automake file for the login authentication module.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src`.

## Control Flow
Build descends into `src`.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrated by `xlators/protocol/auth/Makefile.am`.

## Risks
If omitted, username/password and SSL-name auth module is not built.

## Test Signals
Recursive build should enter `auth/login/src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/login/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/login/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/protocol/auth/login/src/Makefile.am

## Purpose
Defines the build recipe for the login authentication module.

## Important APIs, Types, And Functions
Builds `login.la` from `login.c`, installs it in the auth module directory, links `libglusterfs.la`, and includes libglusterfs, protocol server, and XDR headers.

## Control Flow
Automake compiles a single auth module source with module linker flags.

## State And Persistence
No runtime state; install path controls module discovery.

## Dependencies And Integration Points
Depends on `authenticate.h` from protocol server and libglusterfs dict/logging helpers.

## Risks
Wrong `authdir` or missing server include path prevents dynamic loading or compilation.

## Test Signals
Build should produce `login.la`; protocol server should be able to load the auth module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/login/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/login/src/login.c -->
# sources/distributed-fs/glusterfs/xlators/protocol/auth/login/src/login.c

## Purpose
Implements login-based authentication for protocol/server. It authorizes either SSL-authenticated names through `auth.login.<brick>.ssl-allow` or username/password credentials through `auth.login.<brick>.allow` and `auth.login.<user>.password`, with optional strict rejection when credentials are missing or unmatched.

## Important APIs, Types, And Functions
`gf_auth()` is the module entry point. It reads `ssl-name`, `username`, `password`, `remote-subvolume`, `strict-auth-accept`, allow lists, and per-user password entries. It uses `fnmatch()` for allow-list patterns. `options[]` documents `auth.login.*.allow` and `auth.login.*.password`.

## Control Flow
SSL identity takes precedence and is treated as already authenticated. Non-SSL mode optionally enables strict auth, then requires username/password only when strict mode is set. The code builds an allow-list key for the remote brick, sets default reject for SSL or strict auth when a list exists, tokenizes the allow list by spaces/commas, and accepts on SSL name match or username match plus password match. Without SSL/strict auth, missing credentials or nonmatching allow list can leave the result as `AUTH_DONT_CARE`.

## State And Persistence
No persistent module state. Credentials and policy live in dictionaries supplied per call.

## Dependencies And Integration Points
Uses Gluster dict/data helpers, logging, `gf_asprintf`, `gf_strdup`, `fnmatch`, and the protocol server auth interface. The module is loaded from the auth directory built by its Makefile.

## Risks
The expression assigning username/password result is hard to read and depends on enum truth values. Non-strict non-SSL behavior intentionally allows unauthenticated clients to fall through as `AUTH_DONT_CARE` for compatibility. Password lookup is keyed by username, not brick+username, so per-user password namespace is global in the config dict. Logs can expose connecting usernames and allowed-user lists.

## Test Signals
Cover SSL names with and without `ssl-allow`, wildcard allow patterns, strict and non-strict missing credentials, correct and incorrect passwords, absent remote subvolume, multiple allow-list delimiters, no allow list, and password entries for users with overlapping names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/auth/login/src/login.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/protocol/client/Makefile.am

## Purpose
Top-level Automake file for the protocol client translator.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src`.

## Control Flow
Recursive build descends into `src`.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Integrated by `xlators/protocol/Makefile.am`.

## Risks
If omitted, the protocol client xlator is not built.

## Test Signals
Build should enter `protocol/client/src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/protocol/client/src/Makefile.am

## Purpose
Defines the build recipe for the Gluster protocol client xlator.

## Important APIs, Types, And Functions
Builds `client.la` from `client.c`, helpers, RPC fops, handshake, callback, and common files. Links libglusterfs, gfrpc, and gfxdr. Private headers include `client.h`, memory/message headers, and `client-common.h`.

## Control Flow
Automake compiles all client sources with libglusterfs, RPC/XDR, socket transport, and RPC library include paths.

## State And Persistence
No runtime state. Install path is `xlator/protocol`.

## Dependencies And Integration Points
This module is the client-side protocol endpoint and depends on Gluster core, RPC transport, XDR generated protocol types, and callback handling in `client-callback.c`.

## Risks
The source list must stay synchronized with generated protocol and helper files. Missing RPC libraries would surface as link failures.

## Test Signals
Build should produce loadable `client.la`; protocol handshake and callback actor symbols should resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-callback.c -->
# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-callback.c

## Purpose
Implements client-side handlers for server-to-client Gluster callback RPCs. It decodes callback payloads, converts them into generic upcall structures, forwards child up/down events, and registers the callback actor table for the Gluster callback program.

## Important APIs, Types, And Functions
Actors include `client_cbk_null`, `client_cbk_fetchspec`, `client_cbk_ino_flush`, `client_cbk_cache_invalidation`, `client_cbk_recall_lease`, `client_cbk_child_up`, `client_cbk_child_down`, `client_cbk_inodelk_contention`, and `client_cbk_entrylk_contention`. Decode paths use `xdr_to_generic()` and conversion helpers such as `gf_proto_cache_invalidation_to_upcall()`, `gf_proto_recall_lease_to_upcall()`, and lock-contention converters. `gluster_cbk_actors[]` maps `GF_CBK_*` IDs to functions, and `gluster_cbk_prog` exports program name, number, version, actors, and actor count.

## Control Flow
RPC dispatch calls the actor for the callback ID. Cache invalidation, recall lease, and lock-contention handlers decode XDR from the supplied iovec, build `gf_upcall` payloads, set event types where required, and call `default_notify(this, GF_EVENT_UPCALL, &upcall_data)`. Child up/down callbacks update `clnt_conf_t.child_up` and notify the xlator. All decode paths free XDR-allocated fields and unref dictionaries before returning.

## State And Persistence
Persistent client state touched here is `conf->child_up`. Other data is transient callback-local decoded protocol structs and upcall structs. Upcall consumers above the client handle any cache invalidation or lease state changes.

## Dependencies And Integration Points
Depends on `client.h`, `rpc-clnt.h`, client message IDs, XDR protocol structs, Gluster upcall conversion helpers, `default_notify`, and the RPC client callback program registration mechanism.

## Risks
Handlers rely on `THIS` being the correct client xlator context. Cache invalidation returns `0` even after decode/conversion failures, while other handlers return `ret`; RPC layer expectations should be checked. Missing `event_type` assignment in cache invalidation may be intentional in the converter but is worth verifying against upcall consumers. Memory ownership is manual for XDR strings/xdata and converted dicts.

## Test Signals
Simulate each `GF_CBK_*` actor with valid and malformed XDR. Verify cache invalidation and recall lease reach upper xlators, child up/down toggles `conf->child_up`, lock contention upcalls include domains/names/xdata, all XDR allocations are freed, and unknown/null callbacks log without crashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-callback.c -->
